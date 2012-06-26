"""
generate javascript code from the abstract parsetree representation of a program
"""

from parsetree import *
from jsmap import binaryOps,unaryOps,assignOps,mappedFuncs
from jslib import *

mdict = {}
class_aliases = {}

class BackendException(Exception):

    def __init__(self,detail):
        self.detail = detail

class BackendNotImplementedException(BackendException):

    def __init__(self,detail):
        BackendException.__init__(self,detail)

    def __str__(self):
        return "Cannot generate javascript for: " + self.detail

class BackendInternalErrorException(BackendException):

    def __init__(self,detail):
        BackendException.__init__(self,detail)

    def __str__(self):
        return "JavaScript Backend Generator: " + self.detail

class JavascriptBackend(object):

    def __init__(self):
        self.code = ''
        self.indent = 0
        self.indentstr = '    '
        self.jslib_support = {}
        self.varcount = 0
        self.dependencies = []
        self.namespace = "__main__"
        self.scope = []
        self.module = None
        self.catchvars = []

    def applyNamespace(self,name,**kwargs):
        namespace = self.namespace
        if 'namespace' in kwargs:
            namespace = kwargs['namespace']
        if namespace != "__main__" and namespace != "":
            self.createNamespace(namespace)
            return namespace+"."+name
        return name

    def createNamespace(self,namespace):
        txt = create_namespace(namespace)
        self.add(txt)

    def hasNamespace(self):
        if self.namespace != "__main__":
            return True
        return False

    def getNamespace(self):
        return self.namespace

    def setNamespace(self,namespace):
        self.namespace = namespace

    def pushScope(self,scope):
        return self.scope.append(scope)

    def popScope(self):
        self.scope.pop()

    def pushCatchVar(self,varname):
        self.catchvars.append(varname)

    def getCatchVar(self):
        if len(self.catchvars) == 0:
            raise BackendInternalErrorException("no catch variable")
        return self.catchvars[len(self.catchvars)-1]

    def popCatchVar(self):
        self.catchvars.pop()

    def getInnerScope(self):
        return self.scope[len(self.scope)-1]

    def isGlobal(self,name):
        if name == "__name__":
            return False
        return self.getInnerScope().isGlobal(name) or isinstance(self.getInnerScope(),Module)

    def addGlobal(self,name):
        self.getInnerScope().addGlobal(name)

    # Expression handling
    # these functions return text with the javascript representation of the expression

    def AttributeLookup(self,adef,**kwargs):
        path = self.attributeLookupPath(adef)
        if path:
            mountpoint = self.module.getMountPoint(path)
            if mountpoint:
                return mountpoint
        txt = self.generate(adef.obj)
        txt += '.'
        txt += adef.attr
        return txt


    def attributeLookupPath(self,obj):
        if isinstance(obj,VarName):
            return obj.varname
        if isinstance(obj,AttributeLookup):
            path = self.attributeLookupPath(obj.obj)
            if path:
                return path + "." + obj.attr
            return None
        return None

    def BinaryOp(self,bop,**kwargs):
        op = bop.op
        if op in binaryOps:
            op = binaryOps[op]
        else:
            raise BackendNotImplementedException("Binary Operation("+op+")")
        dependencies = []
        if isinstance(op,tuple):
            dependencies = op[1]
            op = op[0]
        for dependency in dependencies:
            self.addJslibSupport(dependency)
        if op.find("%1") == -1 and op.find("%2") == -1:
            op = "%1 "+op+" %2"
        txt = ''
        if not 'toplevel' in kwargs:
            txt += "("
        lhtxt = self.generate(bop.left)
        rhtxt = self.generate(bop.right)
        txt += self.expand(op,[lhtxt,rhtxt])
        if not 'toplevel' in kwargs:
            txt += ")"
        return txt

    def DictionaryValue(self,dictv,**kwargs):
        txt = '{'
        nr = len(dictv.keyvalues)
        for idx in xrange(0,nr):
            if idx > 0:
                txt += ','
            (key,value) = dictv.keyvalues[idx]
            ktxt = self.generate(key)
            vtxt = self.generate(value)
            txt += ktxt + ":" + vtxt
        txt += '}'
        return txt

    def FunctionCall(self,fcalldef,**extraargs):

        fname = fcalldef.fname
        methodcall = ('targettxt' in extraargs)

        if not methodcall and self.module.getClassMountPoint(fname):
            fname = self.module.getClassMountPoint(fname)

        fname = self.module.applyAliases(fname)
        args = fcalldef.args
        # create a qualified version of the function name (add a suffix specifying the number of arguments)
        # to use in template lookup
        qfname = fname + "." + str(len(args))
        kwargs = fcalldef.kwargs
        keyvalues = []
        dvtxt = None
        for key in kwargs:
            keyvalues.append((key,kwargs[key]))
        if len(keyvalues):
            dv = DictionaryValue(keyvalues)
            dvtxt = 'new Kwarg('+self.DictionaryValue(dv)+')'
            self.addJslibSupport('Kwarg')
        # search for a function mapping, starting with the qualified version
        template = fname



        if methodcall:
            qfname = "." + qfname
            fname = "." + fname

        for name in [qfname,fname]:

            if name in mappedFuncs:

                dependencies = []

                template = mappedFuncs[name]

                if isinstance(template,tuple):
                    dependencies = template[1]
                    template = template[0]

                for libfunc in dependencies:
                    self.addJslibSupport(libfunc)

                if template == None:
                    raise BackendNotImplementedException("Function/Method:" + name)
                else:
                    break

        argtxt = []
        for arg in args:
            argtxt.append(self.generate(arg))
        if dvtxt:
            argtxt.append(dvtxt)
        txt = self.expand(template,argtxt,**extraargs)
        return txt

    def Lambda(self,ldef,**kwargs):
        txt = 'function('
        for index in xrange(0,len(ldef.args)):
            if index > 0:
                txt += ','
            txt += ldef.args[index]
        txt += ') { return '
        txt += self.generate(ldef.body)
        txt += '; }'
        return txt

    def ListComprehension(self,compv,**kwargs):
        tmpname = self.genTmpVarName("comp")
        self.add("var "+tmpname + "= [];")
        self.nl()
        e = ExpressionStatement(MethodCall(VarName(tmpname),"append",[compv.expr],{}))
        block = Block([e])
        generators = compv.generators
        generators.reverse()
        for generator in generators:
            if generator.cond:
                i  = IfStatement([(generator.cond,block)],None)
                block = Block([i])
            if isinstance(generator.itr,FunctionCall) and generator.itr.fname == 'xrange':
                start = generator.itr.args[0]
                end = generator.itr.args[1]
                if len(generator.itr.args)==3:
                    step = generator.itr.args[2]
                else:
                    step = Literal(1)
                f = ForStatement(generator.target,start,end,step,block)
                block = Block([f])
            else:
                f = ForInStatement(generator.target,generator.itr,block)
                block = Block([f])
        self.generate(block)
        return tmpname

    def ListValue(self,listv,**kwargs):
        txt = '['
        nr = len(listv.elements)
        for idx in xrange(0,nr):
            if idx > 0:
                txt += ','
            txt += self.generate(listv.elements[idx])
        txt += ']'
        return txt

    def Literal(self,lit,**kwargs):
        if isinstance(lit.value,bool):
            if lit.value == True:
                return 'true'
            else:
                return 'false'
        elif lit.value == None:
            return 'null'
        else:
            return repr(lit.value)

    def MethodCall(self,mcalldef,**kwargs):
        target = ''
        path = self.attributeLookupPath(mcalldef.target)
        if path:
            path = path + "." + mcalldef.fname
            if path in class_aliases:
                target = class_aliases[path]

        if target == '':
            target = self.generate(mcalldef.target)
        txt = self.FunctionCall(mcalldef,targettxt=target)
        return txt

    def SliceOp(self,sop,**kwargs):
        txt = ''
        txt += self.generate(sop.target)
        txt += '.slice('
        if sop.lwb:
            txt += self.generate(sop.lwb)
        else:
            txt += '0'
        txt += ','
        if sop.upb:
            txt += self.generate(sop.upb)
        else:
            txt += self.generate(sop.target)+".length"
        # if sop.step:
        #     txt += ':'
        #     txt += self.generate(sop.step)
        txt += ')'
        return txt

    def UniOp(self,uop,**kwargs):
        txt = ''
        if not 'toplevel' in kwargs:
            txt += "("
        op = uop.op
        if op in unaryOps:
            op = unaryOps[op]
        else:
            raise BackendNotImplementedException("Unary Operation("+op+")")
        dependencies = []
        if isinstance(op,tuple):
            dependencies = op[1]
            op = op[0]
        for dependency in dependencies:
            self.addJslibSupport(dependency)
        txt += (op+' ')
        txt += self.generate(uop.arg)
        if not 'toplevel' in kwargs:
            txt += ")"
        return txt

    def VarName(self,vdef,**kwargs):
        name = vdef.varname
        if self.isGlobal(name):
            return self.applyNamespace(name)
        mountpoint = self.module.getClassMountPoint(name)
        if mountpoint:
            return mountpoint
        return name

    # Statement handling
    # these methods do not return values but update the output program using the methods

    def AssignmentStatement(self,adef,**kwargs):
        if isinstance(adef.target, SliceOp):
            self.AssignmentSliceStatement(adef,**kwargs)
            return
        if isinstance(adef.target, ListValue):
            self.MultiAssignmentStatement(adef,**kwargs)
            return
        class_variable = False
        target = adef.target
        if not isinstance(target,AttributeLookup):
            self.declare(adef.target)
        varname = self.generate(target)
        exprtxt = self.generate(adef.expr,toplevel=True)
        self.add(varname)
        self.add('=')
        self.add(exprtxt)
        self.add(';')

    def AssignmentSliceStatement(self,adef,**kwargs):
        lwb = adef.target.lwb
        upb = adef.target.upb
        step = adef.target.step

        targettxt = self.generate(adef.target.target)
        exprtxt = self.generate(adef.expr)

        varname_s = self.genTmpVarName("slice")
        varname_l = self.genTmpVarName("loop")
        varname_c = self.genTmpVarName("counter")

        if lwb:
            if isinstance(lwb,VarName) or isinstance(lwb,Literal):
                lwbtxt = self.generate(lwb)
            else:
                lwbtxt = self.genTmpVarName("lwb")
                self.add("var "+lwbtxt+"="+self.generate(lwb,toplevel=True)+";").nl()
        else:
            lwbtxt = "0"

        varname_u = self.genTmpVarName("upb")
        if upb:
            self.add("var "+varname_u+"="+self.generate(upb,toplevel=True)+";").nl()
        else:
            self.add("var "+varname_u+"="+targettxt+".length;").nl()

        if step:
            if isinstance(step,VarName) or isinstance(step,Literal):
                steptxt = self.generate(step)
            else:
                steptxt = self.genTmpVarName("step")
                self.add("var "+steptxt+"="+self.generate(step,toplevel=True)+";").nl()
        else:
            steptxt = "1"

        self.add("var "+varname_s+"="+exprtxt+";").nl();
        self.add("var "+varname_l+";").nl()
        self.add("var "+varname_c+"=0;").nl()

        self.add("for("+varname_l+"="+lwbtxt+";"+varname_l+"<"+varname_u+";"+varname_l+"+="+steptxt+" ) {")
        self += 1

        self.nl().add("if ( "+varname_c+" < "+varname_s+".length) {")
        self += 1
        self.nl()
        self.add(targettxt+"["+varname_l+"] = " + varname_s + "["+varname_c+"];")
        self -= 1
        self.nl().add("} else {")
        self += 1
        self.nl().add(targettxt+".splice("+varname_l+",1);")
        self.nl().add(varname_l+"--;")
        self.nl().add(varname_u+"--;")
        self -= 1
        self.nl().add("}").nl().add(varname_c+"++;")
        self -= 1
        self.nl()
        self.add("}").nl()
        self.add("while ( "+varname_c+" < "+varname_s+".length) {")
        self += 1
        self.nl().add(targettxt+".splice("+varname_l+",0," + varname_s + "["+varname_c+"]);")
        self.nl().add(varname_c+"++;")
        self.nl().add(varname_l+"++;")
        self -= 1
        self.nl().add("}")

    def AugmentedAssignmentStatement(self,adef,**kwargs):
        target = adef.target
        if not isinstance(target,AttributeLookup):
            self.declare(adef.target)
        vtxt = self.generate(target)
        etxt = self.generate(adef.expr,toplevel=True)
        op = adef.op
        if op in assignOps:
            op = assignOps[op]
        else:
            print str(assignOps)
            raise BackendNotImplementedException("Augmented Assignment Operation("+op+")")
        dependencies = []
        if isinstance(op,tuple):
            dependencies = op[1]
            op = op[0]
        for dependency in dependencies:
            self.addJslibSupport(dependency)
        txt = self.expand(op,[vtxt,etxt])
        self.add(txt+";")

    def MultiAssignmentStatement(self, adef, **kargs):
        class_variable = False
        target = adef.target
        if not isinstance(target,AttributeLookup):
            self.declare(adef.target)
        varname = self.generate(target)
        exprtxt = self.generate(adef.expr,toplevel=True)
        tmpv = self.genTmpVarName("assigment")
        self.add(tmpv)
        self.add('=')
        self.add(exprtxt)
        self.add(';\n')

        self.add(self.distructure(adef.target, tmpv))

    def Block(self,block,**kwargs):
        if not 'toplevel' in kwargs:
            self.openBlock()
        if 'extras' in kwargs:
            for e in kwargs['extras']:
                self.add(e)
                self.nl()
        for a in xrange(0,len(block.statements)):
            statement = block.statements[a]
            self.generate(statement)
            if a != len(block.statements)-1:
                self.nl()
        if not 'toplevel' in kwargs:
            self.closeBlock()

    def BreakStatement(self,breakdef,**kwargs):
        self.add('break;')

    def ClassDefinitionStatementStubGenericBody(self,memberfn,namespace,fname,**kwargs):
        instname = "this"
        if 'instname' in kwargs:
            instname = kwargs['instname']
        constructor = False
        if 'constructor' in kwargs:
            constructor = kwargs['constructor']
        btxts = []
        if 'staticmethod' in memberfn.decorators:
            btxts.append("args = [];")
        else:
            btxts.append("args = ["+instname+"];")
        btxts.append("for(var a=0;a<arguments.length;a++) {")
        btxts.append(self.indentstr+"args.push(arguments[a]);")
        btxts.append("}")
        retline = ""
        if not constructor:
            retline += "return "
        retline += self.applyNamespace(fname,namespace=namespace)+".apply(null,args);"
        btxts.append(retline)
        return btxts

    def ClassDefinitionStatementStub(self,memberfn,namespace,fname,**kwargs):
        objname = "self"
        if 'objname' in kwargs:
            objname = kwargs['objname']
        instname = "this"
        if 'instname' in kwargs:
            instname = kwargs['instname']
        isstatic = False
        if 'staticmethod' in memberfn.decorators:
            isstatic = True
        if memberfn.kwarg != None or memberfn.vararg != None:
            factxts = []
            factxts.append(objname+"."+fname+" = function() {")
            btxts = self.ClassDefinitionStatementStubGenericBody(memberfn,namespace,fname,instname=instname)
            for btxt in btxts:
                factxts.append(self.indentstr+btxt)
            factxts.append("}")
            return factxts
        else:
            factxt = objname+"."+fname+ " = function("
            argtxt = ""
            startarg=1
            if isstatic:
                startarg=0
            for idx in xrange(startarg,len(memberfn.argnames)):
                if idx > 1:
                    argtxt += ","
                argtxt += memberfn.argnames[idx]
            factxt += argtxt
            factxt += ") { return " + self.applyNamespace(fname,namespace=namespace)
            if isstatic:
                factxt += "("+argtxt+")"
            else:
                if argtxt != "":
                    argtxt = ","+argtxt
                factxt += "("+instname+argtxt+")"
            factxt += "; }"
            return [factxt]

    def ClassDefinitionStatement(self,cdef,**kwargs):

        self.pushScope(cdef)

        original_namespace = self.getNamespace()

        namespace = cdef.getClassNamespace()

        if cdef.parent_class:
            parent_namespace = cdef.parent_class.getClassNamespace()
        else:
            parent_namespace = original_namespace

        # generate the namespace apart from the inner most one (which
        # will be created by the factory function of this class)

        nstxt = create_namespace(namespace,True)
        self.add(nstxt)
        self.nl()

        self.setNamespace(parent_namespace)

        # generate the factory function, a function with the same name as the class, that
        # will construct a new class instance
        decorators = []
        ctrargs = []
        ctrvararg = None
        ctrkwarg = None
        if cdef.constructor:
            decorators = cdef.constructor.decorators
            ctrargs = cdef.constructor.argnames[1:]
            ctrvararg = cdef.constructor.vararg
            ctrkwarg = cdef.constructor.kwarg

        facbody = []
        facbody.append(Verbatim("if (arguments.length==1 && arguments[0] == undefined) { return; }"))
        facbody.append(Verbatim("var self = new "+self.applyNamespace(cdef.cname)+"(undefined);"))

        self.setNamespace(namespace)

        # hook up member functions as properties of the class instance
        fns = cdef.memberfns()
        for fname in fns:
            (ns,memberfn) = fns[fname]
            stubs = self.ClassDefinitionStatementStub(memberfn,ns,fname)
            for stub in stubs:
                facbody.append(Verbatim(stub))

        # hook up factory functions for inner classes as properties of the class instance
        # FIXME need to do this recursively?
        innerclasses = cdef.innerclasslist()
        for (innerclass,innernamespace) in innerclasses:
            txt = "self."+innerclass.cname+"="+innernamespace+"."+innerclass.cname+";"
            facbody.append(Verbatim(txt))

        # if the class has a constructor, need to call it towards the end of the factory function
        if cdef.constructor:
            if cdef.constructor.kwarg != None or cdef.constructor.vararg != None:
                btxts = self.ClassDefinitionStatementStubGenericBody(cdef.constructor,
                                                            cdef.cname,cdef.constructor.fname,instname='self',constructor=True)
                for btxt in btxts:
                    facbody.append(Verbatim(btxt))
            else:
                ctrcall = ""
                ctrcall += self.applyNamespace(cdef.constructor.fname)
                ctrcall += "(self"
                argtxt = ""
                for idx in xrange(1,len(cdef.constructor.argnames)):
                    if idx > 1:
                        argtxt += ","
                    argtxt += cdef.constructor.argnames[idx]
                if argtxt != "":
                    argtxt = ","+argtxt
                ctrcall += argtxt + ");"
                facbody.append(Verbatim(ctrcall))

        facbody.append(Verbatim("return self;"))
        self.nl()
        # factory function defined

        self.setNamespace(parent_namespace)

        # now create a dummy FunctionDefinitionStatement to generate the factory function
        facfn = FunctionDefinitionStatement(cdef.cname)

        facfn.configure(decorators,
                    ctrargs,
                    [],
                    ctrvararg,
                    ctrkwarg,
                    Block(facbody))
        self.generate(facfn)
        self.nl()
        self.nl()

        self.setNamespace(namespace)

        # generate the defintion for the class __init__ constructor (if it exists)
        if cdef.constructor:
            # self.generate(cdef.constructor,class_owner=cdef.cname)
            self.generate(cdef.constructor)
            self.nl()

        # generate definitions for all other member and static class functions
        for fname in fns:
            (classname,memberfn) = fns[fname]

            if classname==cdef.getClassNamespace():
                # only generate functions which are defined on this class (not inherited ones)
                self.generate(memberfn)
                self.nl()
            else:
                # for inherited, static methods need to note an alias for rewriting callers
                if 'staticmethod' in memberfn.decorators:
                    key = cdef.getClassNamespace()+"."+fname
                    alias = classname
                    class_aliases[key] = alias
                    self.add( "/* "+key+"->"+alias+" */" )
                    self.nl()

        # generate static class variables now
        for (target,expr) in cdef.staticmembervars:
            if isinstance(target,VarName):
                self.addGlobal(target.varname)
            a = AssignmentStatement(target,expr)
            self.generate(a)
            self.nl()

        self.ClassSuperMethod(cdef,**kwargs)

        self.setNamespace(original_namespace)

        self.popScope()


    def ClassSuperMethod(self,cdef,**kwargs):
        # generate an object used to dispatch super(<thisclass>,instance) cals

        name = cdef.getClassNamespace()
        self.add(name+".super = function(self) {")
        self += 1
        self.nl();
        self.add("this.self = self;");
        self.nl();

        fns = cdef.memberfns(True)
        for fname in fns:
            (ns,memberfn) = fns[fname]
            stubs = self.ClassDefinitionStatementStub(memberfn,ns,fname,objname='this',instname='this.self')
            for stub in stubs:
                self.add(stub)
                self.nl()
        self -= 1
        self.add("return this;")
        self.nl()
        self.add("}")
        self.nl()


    def ContinueStatement(self,continuedef,**kwargs):
        self.add('continue;')

    def DeclareStatement(self,ddef):
        if len(ddef.declarevars):
            self.add("var ");
            for index in xrange(0,len(ddef.declarevars)):
                if index > 0:
                    self.add(",")
                self.add(ddef.declarevars[index])
            self.add(";")

    def DeleteStatement(self,ddef):
        if isinstance(ddef.target,SliceOp):
            self.generate(AssignmentStatement(ddef.target,ListValue([])))
        elif isinstance(ddef.target,BinaryOp) and ddef.target.op == '[]':
            lefttxt = self.generate(ddef.target.left)
            righttxt = self.generate(ddef.target.right)
            self.add("if ("+lefttxt+" instanceof Array) {")
            self += 1
            self.nl().add(lefttxt + ".splice(" + righttxt + ",1);")
            self -= 1
            self.nl().add("} else {")
            self += 1
            self.nl().add("delete "+lefttxt+"["+righttxt+"]")
            self -= 1
            self.nl().add("}")
        else:
            targettxt = self.generate(ddef.target,toplevel=True)
            self.add("delete " + targettxt);

    def EmptyStatement(self,edef,**kwargs):
        # add a comment to make the resulting javascript a little more readable
        self.add("/* pass */")

    def ExceptionHandlerStatement(self,hdef,**kwargs):
        e = []
        catchvar = self.getCatchVar()
        index = kwargs['handler_index']
        if hdef.ename:
            if hdef.etype:
                if index == 0:
                    self.add("if ")
                else:
                    self.add(" else if ")
                self.add("(" + catchvar + " instanceof " + hdef.etype + ")")

            if hdef.ename != catchvar:
                e.append("var "+hdef.ename+"="+catchvar+";")
        else:
            if index > 0:
                self.add(" else ")
        self.generate(hdef.ebody,extras=e)

    def ExpressionStatement(self,edef,**kwargs):
        self.add(self.generate(edef.expr,toplevel=True))
        self.add(';')

    def ForStatement(self,fordef,**kwargs):
        self.declare(fordef.varname)
        lwbtxt = self.generate(fordef.lwb)
        upbtxt = self.generate(fordef.upb)
        steptxt = self.generate(fordef.step)
        varname = self.generate(fordef.varname)
        self.add('for(')
        self.add(varname+'='+lwbtxt+';')
        self.add(varname+'<'+upbtxt+';')
        self.add(varname +'+=' + steptxt +')')
        self.generate(fordef.block)

    def ForInStatement(self,fordef,**kwargs):
        self.declare(fordef.target)
        self.addJslibSupport('Generator')
        tmp = self.genTmpVarName("container")
        a = AssignmentStatement(VarName(tmp),fordef.container)
        self.generate(a)
        self.nl();
        tmpv = self.genTmpVarName("generator")
        self.add('var '+tmpv+' = new Generator('+tmp+');')
        self.nl()
        e = []
        if isinstance(fordef.target,ListValue):
            varname = self.genTmpVarName("loop")
            if isinstance(fordef.target, ListValue):
                e.append(self.distructure(fordef.target, varname))
            else:
                txt = self.generate(fordef.target)
                txt += "="
                txt += varname
                txt += ";"
                e.append(txt)
        else:
            varname = self.generate(fordef.target)

        self.add('for(')
        self.add(varname+'='+tmpv+'.nextValue();'+tmpv+'.hadMore();'+varname+'='+tmpv+'.nextValue())')
        self.generate(fordef.block,extras=e)


    def FunctionDefinitionStatement(self,funcdef,**kwargs):
        self.pushScope(funcdef)
        name = funcdef.fname

        if self.hasNamespace():
            nsname = self.applyNamespace(name)
            self.add(create_namespace(nsname,True))
            txt =  nsname + " = function("
        else:
            txt = "function "+name+"("
        argc = len(funcdef.argnames)
        for a in xrange(0,argc):
            if a>0:
               txt += ","
            argname=funcdef.argnames[a]

            txt+=argname
        txt += ") "
        self.add(txt)
        e = []

        if len(funcdef.argdefaults):
            offset = len(funcdef.argnames) - len(funcdef.argdefaults)
            for di in xrange(0,len(funcdef.argdefaults)):
                argname = funcdef.argnames[di+offset]
                e += ['if ('+argname+' == undefined) {']
                e += ['   '+argname+'='+self.generate(funcdef.argdefaults[di],toplevel=True)+';']
                e += ['}']

        if funcdef.kwarg or funcdef.vararg:
            tmpv_len = self.genTmpVarName()
            e += ['var ' + tmpv_len + '= arguments.length;']

        if funcdef.kwarg:
            self.addJslibSupport('Kwarg')
            tmpv_lastarg = self.genTmpVarName()
            e += ['var ' + tmpv_lastarg + '= arguments[arguments.length-1];']
            e += ['var ' + funcdef.kwarg + ' = {};']
            e += ['if (' + tmpv_lastarg + ' instanceof Kwarg) {']
            e += ['    ' + funcdef.kwarg + ' = ' + tmpv_lastarg + '.getDict();']
            e += ['    ' + tmpv_len + '--;']
            e += [' } ']
        if funcdef.vararg:
            tmpv = self.genTmpVarName()
            e += ['var '+funcdef.vararg + '= [];']
            e += ['for('+tmpv+'='+str(argc)+';'+tmpv+'<'+tmpv_len+';'+tmpv+'++) {']
            e += ['    ' + funcdef.vararg + '.push(arguments['+tmpv+']);']
            e += ['}']
        self.generate(funcdef.block,extras=e)
        self.popScope()


    def GlobalStatement(self,gdef,**kwargs):
        self.addGlobal(gdef.varname)

    def IfStatement(self,ifdef,**kwargs):
        idx = 0
        for test in ifdef.tests:
            cond, block = test
            if idx == 0:
                self.add("if (")
            else:
                self.add("else if (")
            self.add(self.generate(cond,toplevel=True))
            self.add(")")
            self.generate(block)
        if ifdef.elseblock:
            self.add("else ")
            self.generate(ifdef.elseblock)

    def Module(self,mdef,**kwargs):
        original_scope = self.scope
        self.scope = []
        self.pushScope(mdef)
        original_module = self.module
        self.module = mdef

        header = "// generated by pystorm from "+mdef.path + "\n\n\n"
        trailer = ""
        if mdef.name == '__main__':
            header += "var __name__ = '__main__';\n\n"
        else:
            header += "__name__ = '"+mdef.namespace+"';\n\n"
            trailer += "\n\n\n__name__ = '"+self.namespace+"';\n\n"

        self.add(header)

        if mdef.name=='__main__' or (len(mdef.aliases)==1 and mdef.aliases[0][0]=='*'):
            # "from <module> import *": inline the module completely
            self.generate(mdef.code,toplevel=True)
            self.nl()
        else:
            original_namespace = self.namespace
            self.namespace = mdef.namespace
            self.nl()
            self.add("// "+original_namespace + "->" + self.namespace)
            self.nl()
            self.generate(mdef.code,toplevel=True)
            self.nl()
            self.namespace = original_namespace
            # raise BackendNotImplementedException("import other than 'from <module> import *'")

        self.add(trailer)
        self.scope = original_scope
        self.module = original_module

    def PrintStatement(self,printdef,**kwargs):
        self.add("console.log(")
        for a in xrange(0,len(printdef.values)):
            if a>0:
                self.add('+ " " +')
            self.add('String(')
            self.add(self.generate(printdef.values[a]))
            self.add(')')
        self.add(');')

    def RaiseStatement(self,rdef,**kwargs):
        self.add("throw ")
        if rdef.rtype:
            self.add(self.generate(rdef.rtype))
            if rdef.robj:
                self.add("(")
                self.add(self.generate(rdef.robj))
                self.add(")")
        else:
            catchvar = self.getCatchVar()
            self.add(catchvar)
        self.add(";")

    def ReturnStatement(self,retdef,**kwargs):
        self.add('return')
        if retdef.value:
            self.add(' ')
            self.add(self.generate(retdef.value))
        self.add(';')

    def TryStatement(self,trydef,**kwargs):
        self.add("try")
        self.generate(trydef.body)
        if len(trydef.handlers)>0:

            catchvar = self.genTmpVarName("ex")
            self.add("catch")
            self.add("("+catchvar+")")
            self.add("{")
            self += 1
            self.nl()

            for idx, handler in enumerate(trydef.handlers):
                if handler.name:
                    self.add("var "+handler.name.id+"="+catchvar+";")
                
            for idx, handler in enumerate(trydef.handlers):
                self += 1
                self.nl()

                if handler.name:
                    if idx != 0:
                        self.add("else ")
                    self.add("if("+handler.name.id+" instanceof "+handler.type.id+")")
                    self.nl()
                else:
                    if idx != 0:
                        self.add("else ")
                    else:
                        self.add("if(true)")

                #if handler.name:
                #    catchvar = handler.name.id
                #if catchvar == None:
                #    catchvar = self.genTmpVarName("ex")

                self.pushCatchVar(catchvar)
                catchall = False
                if len(trydef.handlers)==1 and trydef.handlers[0].name == None:
                    catchall = True
                #if not catchall:
                #    self.openBlock()
                self.generate(handler.body, handler_index=idx)
                #if not catchall:
                #    self.closeBlock()
                self.popCatchVar()
                self -= 1
                self.nl()
            self -= 1
            self.nl()
            self.add("}")
        if trydef.final:
            self.add("finally")
            self.generate(trydef.final)

    def WhileStatement(self,whiledef,**kwargs):
        self.add('while(')
        self.add(self.generate(whiledef.cond,toplevel=True))
        self.add(')')
        self.generate(whiledef.block)

    def Verbatim(self,vdef,**kwargs):
        textlines = vdef.text.split('\n')
        for textline in textlines:
            self.nl()
            self.add(textline)

    # Common

    def generate(self,code,**kwargs):
        return getattr(self,code.__class__.__name__)(code,**kwargs)

    def declare(self,target):
        walker = VarNameWalker()
        target.walk(walker)
        varnames = walker.getVarNames()
        declares = []
        for varname in varnames:
            if not self.isGlobal(varname):
                declares.append(varname)
        decl = DeclareStatement(declares)
        self.generate(decl)
        self.nl()

    def nl(self):
        self.add('\n')
        for i in xrange(0,self.indent):
            self.add(self.indentstr)
        return self

    def add(self,str):
        self.code += str
        return self

    def __add__(self,num):
        self.indent += num
        return self

    def openBlock(self):
        self.add(" {")
        self += 1
        self.nl()
        return self

    def closeBlock(self):
        self -= 1
        self.nl()
        self.add("}")
        return self

    def __sub__(self,num):
        self.indent -= num
        return self

    def getCode(self):
        final_code = ''
        for package in self.jslib_support:
            entry = pystorm_lib[package]
            if entry.startswith("file:"):
                path = entry[5:]
                f = open(path,"r")
                entry = f.read()
            final_code += entry
            final_code += "\n\n"
        final_code += self.code
        return final_code

    def expand(self,template,parameters,**kwargs):
        # check to see if there is a target object (or class) associated with the call
        targettxt = ''
        if 'targettxt' in kwargs:
            targettxt = kwargs['targettxt']
        # create the default placeholders string eg (%1,%2,%3) if there are 3 parameters
        placeholders = ""
        for index in xrange(0,len(parameters)):
                if index > 0:
                    placeholders += ','
                placeholders += '%'
                placeholders += str(index+1)
        # create the template to expand
        if template.find('%') == -1 and template.find('(') == -1:
            template += '('+placeholders+')'
        elif template.find('%*'):
            template = template.replace('%*',placeholders)
        # compile a list of the position of each placeholder %1, %2, ... and its index in the template
        matches = []
        startindex = 1
        if targettxt != '':
            startindex = 0
        for index in xrange(startindex,len(parameters)+1):
            placeholder = '%'+str(index)
            pos = 0
            while pos > -1:
                pos = template.find(placeholder,pos)
                if pos > -1:
                    matches.append((pos,index-1))
                    pos += 1
        # sort the matches into reverse order (ones at the end of the template occuring earlier)
        def matchsort(x,y):
            if x[0] < y[0]:
                return 1
            if x[0] == y[0]:
                return 0
            return -11
        matches.sort(matchsort)
        # convert the template from a string to a list ready to manipulate
        expansion = list(template)
        # work backwards through the string swapping placeholders for parameters
        maptarget=False
        for (pos,index) in matches:
            if index >= 0:
                expansion[pos:pos+2] = list(parameters[index])
            else:
                # found a %0 to match
                expansion[pos:pos+2] = targettxt
                # note that we are switching from a method call to a function call
                # with the target mapped to a parameter
                maptarget=True
        # convert back to a string and return
        txt = ''
        if targettxt != '' and not maptarget:
            # make an instance call or a static function call (if the target is a class name)
            txt += targettxt
            txt += "."
        txt += ''.join(expansion)
        return txt

    def distructure(self, varlist, mainvar):
        t = []
        for i, var in enumerate(varlist.elements):
            t.append(var.varname)
            t.append('=')
            t.append(mainvar)
            t.append("[")
            t.append(str(i))
            t.append("]")
            t.append(';')
        return "".join(t)


    def unpackListValue(self,target,varname,assignments):
        if isinstance(target,ListValue):
            for idx in xrange(0,len(target.elements)):
                self.unpackListValue(target.elements[idx],varname+"["+str(idx)+"]",assignments)
        elif isinstance(target,VarName):
            txt = ""
            # if target.isdecl:
            txt +=  "var "
            txt += self.generate(target)
            txt += "="
            txt += varname
            txt += ";"
            assignments.append(txt)
        elif isinstance(target,AttributeLookup):
            txt = self.generate(target)
            txt += "="
            txt += varname
            txt += ";"
        else:
            assert False

    def insertDependency(self,line):
        self.dependencies = [line] + self.dependencies

    def generateDependencies(self):
        for dependency in self.dependencies:
            self.add(dependency)
            self.nl()
        self.dependencies = []

    def addJslibSupport(self,package):
        self.jslib_support[package] = True

    def genTmpVarName(self,prefix=''):
        self.varcount += 1
        return prefix+"_pystorm_"+str(self.varcount)

def create_namespace(module,skiplast=False):
    txt = ""
    names= module.split(".")
    global mdict
    path = ""
    max = len(names)
    if skiplast:
        max -= 1
    for x in xrange(0,max):
        if x > 0:
            path += "."
        path = path+names[x]
        if path not in mdict:
            if x == 0:
                txt += "var "
            txt += path
            txt += " = {};\n"
            mdict[path] = ""
    mdict[module] = ""
    return txt

# write a module
def jswrite(code,pypath):
    global mdict
    mdict.clear()
    class_aliases.clear()
    jb = JavascriptBackend()
    jb.generate(code)
    return jb.getCode()

