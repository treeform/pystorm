"""
call the python built-in compile to convert a python program to an ast structure, then convert that structure
to a simplified structure using the classes in parsetree.py
"""

from parsetree import *

import _ast
from os.path import split, splitext, join
import codecs
import sys
from jslib import pystorm_modules

loaded_modules = set()
global initial_module_dir
initial_module_dir = ''

class FrontendException(Exception):

    def __init__(self,detail,lineno):
        self.detail = detail
        self.lineno = lineno

class FrontendNotHandledException(FrontendException):

    def __init__(self,detail,lineno):
        FrontendException.__init__(self,detail,lineno)

    def __str__(self):
        return "Cannot convert python code at line "+str(self.lineno)+": "+ self.detail

class FrontendInternalException(FrontendException):

    def __init__(self,detail,lineno):
        FrontendException.__init__(self,detail,lineno)

    def __str__(self):
        return "Python parser internal error "+str(self.lineno)+": "+ self.details


class GenVisitor(object):

    def __init__(self,module_name,module_path,module_namespace):
        self.uops = { 'Not':'not', 'UAdd':'+', 'USub':'-', 'Invert':'~' }
        self.bops = { 'Eq':"==", 'NotEq':'!=', 'Mult':"*", 'Sub':"-", 'Lt':'<', 'LtE':'<=', 'Gt':'>', 'GtE':'>=', 'Add':'+', 'Mod':'%', 'And':'and', 'Or':'or', 'Div':'/', 'Pow':'**', 'In':'in', 'NotIn':'not in', 'RShift':'>>', 'LShift':'<<', 'BitOr':'|', 'BitXor':'^', 'BitAnd':'&', 'FloorDiv':'//' }
        self.aops = { 'Add':'+=', 'Sub':'-=', 'Mult':'*=', 'Div':'/=', 'Mod':'%=', 'Pow':'**=', 'RShift':'>>=', 'LShift':'<<=', 'BitOr':'|=', 'BitXor':'^=', 'BitAnd':'&=', 'FloorDiv':'//=' }
        self.module = None
        self.module_name = module_name
        self.module_path = module_path
        self.module_namespace = module_namespace
        self.scope = []

    def parse(self,contents):
        ast = compile(contents, '<string>', 'exec', _ast.PyCF_ONLY_AST)
        return self.visit(ast)

    def visit(self,ast):
        if ast == None:
            return None
        name = ast.__class__.__name__
        if hasattr(self,name):
            return getattr(self,name)(ast)
        else:
            raise FrontendNotHandledException("No handler for AST object: "+name,ast.lineno)

    def pushScope(self,scope):
        return self.scope.append(scope)

    def popScope(self):
        self.scope.pop()

    def getInnerScope(self):
        return self.scope[len(self.scope)-1]

    def isGlobal(self,name):
        return self.getInnerScope().isGlobal(name)

    def addGlobal(self,name):
        self.getInnerScope().addGlobal(name)

# expressions

    def Attribute(self,ast):
        obj = self.visit(ast.value)
        attr = ast.attr
        return AttributeLookup(obj,attr)

    def BinOp(self,ast):
        op = self.bops[ast.op.__class__.__name__]
        lhs = self.visit(ast.left)
        rhs = self.visit(ast.right)
        return BinaryOp(op,lhs,rhs)

    def BoolOp(self,ast):
        op = self.bops[ast.op.__class__.__name__]
        values = ast.values
        assert(len(values)>1)
        for idx in xrange(0,len(values)):
            values[idx] = self.visit(values[idx])
        expr = None
        start = len(values)-2
        while start >= 0:
            if expr == None:
                expr = BinaryOp(op,values[start],values[start+1])
            else:
                expr = BinaryOp(op,values[start],expr)
            start -= 1
        return expr

    def Call(self,ast):
        args = []
        kwargs = {}
        for keyword in ast.keywords:
            key = VarName(keyword.arg)
            kwargs[key] = self.visit(keyword.value)
        for a in xrange(0,len(ast.args)):
            arg = self.visit(ast.args[a])
            args.append(arg)
        if ast.func.__class__.__name__ == 'Attribute':
            target = self.visit(ast.func.value)
            return MethodCall(target,ast.func.attr,args,kwargs)
        fname = ast.func.id
        return FunctionCall(fname,args,kwargs)

    def Compare(self,ast):
        result = None
        lhs = self.visit(ast.left)
        for index in xrange(0,len(ast.ops)):
            op = self.bops[ast.ops[index].__class__.__name__]
            rhs = self.visit(ast.comparators[index])
            clause = BinaryOp(str(op),lhs,rhs)
            if result == None:
                result = clause
            else:
                result = BinaryOp("and",result,clause)
            lhs = rhs
        return result

    def comprehension(self, ast):
        t = self.visit(ast.target)
        i = self.visit(ast.iter)
        cond = None
        for e in ast.ifs:
            target = self.visit(e.left)
            # print str(e.__dict__)
            for index in xrange(0,len(e.ops)):
                c = self.visit(e.comparators[index])
                op = e.ops[index].__class__.__name__
                if op in self.bops:
                    op = self.bops[op]
                else:
                    raise FrontendNotHandledException('Binary Operaton:'+op,ast.lineno)
                bop = BinaryOp(op,target,c)
                if cond:
                    cond = BinaryOp('and',cond,bop)
                else:
                    cond = bop
        return ListComprehensionGenerator(t,i,cond)

    def Dict(self, ast):
        keyvals = []
        for idx in xrange(0,len(ast.keys)):
            key = ast.keys[idx]
            value = ast.values[idx]
            keyvals.append((self.visit(key),self.visit(value)))
        return DictionaryValue(keyvals)

    def Expr(self, ast):
        expr = self.visit(ast.value)
        return [ExpressionStatement(expr)]

    def GeneratorExp(self, ast):
        # it seems that generator expressions can be handled
        # in the same way as list comprehensions!
        return self.ListComp(ast)

    def Index(self,ast):
        return self.visit(ast.value)

    def Lambda(self, ast):
        args = []
        for a in ast.args.args:
            args.append(a.id)
        body = self.visit(ast.body)
        return Lambda(args,body)

    def List(self,ast):
        elements = []
        for e in ast.elts:
            elements.append(self.visit(e))
        return ListValue(elements)

    def ListComp(self, ast):
        e = self.visit(ast.elt)
        generators = []
        for g in ast.generators:
                generators.append(self.visit(g))
        return ListComprehension(e,generators)

    def Name(self,ast):
        if ast.id == 'True':
            return Literal(True)
        elif ast.id == 'False':
            return Literal(False)
        elif ast.id == 'None':
            return Literal(None)
        return VarName(ast.id)

    def Num(self,ast):
        return Literal(ast.n)

    def Slice(self,ast):
        return (self.visit(ast.lower),self.visit(ast.upper),self.visit(ast.step))

    def Str(self,ast):
        return Literal(ast.s)

    def Subscript(self,ast):
        op = "[]"
        arg = self.visit(ast.value)
        index = self.visit(ast.slice)
        if isinstance(index,tuple):
            # slice operation
            return SliceOp(arg,index)
        else:
            return BinaryOp(op,arg,index)

    def Tuple(self,ast):
        return self.List(ast)

    def UnaryOp(self,ast):
        op = self.uops[ast.op.__class__.__name__]
        arg = self.visit(ast.operand)
        return UniOp(op,arg)

# Blocks and statements

    def makeBlock(self,code):
        if not (isinstance(code,Block)):
            return Block([code])
        else:
            return code

    def Assign(self, ast):
        if len(ast.targets) != 1:
            raise FrontendNotHandledException('Multiple targets in assignment',ast.lineno)
        target = self.visit(ast.targets[0])
        expr = self.visit(ast.value)
        adef = AssignmentStatement(target, expr)
        return [adef]

    def AugAssign(self, ast):
        target = self.visit(ast.target)
        op = self.aops[ast.op.__class__.__name__]
        expr = self.visit(ast.value)
        adef = AugmentedAssignmentStatement(target, op, expr)
        return [adef]

    def Break(self,ast):
        bdef = BreakStatement()
        return [bdef]

    def ClassDef(self,ast):
        name = ast.name
        subclasses = []
        bases = []
        for base in ast.bases:
            bases.append(base.id)
        memberfns = []
        staticvars = []
        constructor = None
        cdef = ClassDefinitionStatement(name,self.module)
        self.pushScope(cdef)
        for stmt in ast.body:
            stmts = self.visit(stmt)
            for b in stmts:
                if isinstance(b,FunctionDefinitionStatement):
                    if b.fname == '__init__':
                        constructor = b
                    else:
                        memberfns.append(b)
                elif isinstance(b,ClassDefinitionStatement):
                    b.setParentClass(cdef)
                    subclasses.append(b)
                elif isinstance(b,AssignmentStatement):
                    staticvars.append((b.target,b.expr))
                elif isinstance(b,EmptyStatement):
                    pass
                elif isinstance(b,ExpressionStatement):
                    pass # perhaps a docstring?  FIXME - need to check
                else:
                    raise FrontendNotHandledException("class contents except for member variables, classes and functions",ast.lineno)
        cdef.configure(bases,constructor,memberfns,staticvars,subclasses)
        self.module.addClassMountPoint(name,cdef.getClassNamespace())
        self.popScope()
        return [cdef]+subclasses

    def Continue(self,ast):
        cdef = ContinueStatement()
        return [cdef]

    def Delete(self, d):
        dels = []
        for target in d.targets:
            dels.append(DeleteStatement(self.visit(target)))
        return dels

    def excepthandler(self, ast):
        etype = None
        if ast.type:
            etype = ast.type.id
        ename = None
        if ast.name:
            ename = ast.name.id
        body = self.Statements(ast.body)
        edef = ExceptionHandlerStatement(etype,ename,body)
        return edef

    def For(self, ast):
        target = self.visit(ast.target)
        loopexpr = self.visit(ast.iter)
        body = self.Statements(ast.body)
        if isinstance(loopexpr,FunctionCall):
            if loopexpr.fname == "xrange" or loopexpr.fname == 'range':
                lwb = loopexpr.args[0]
                upb = loopexpr.args[1]
                if len(loopexpr.args)==3:
                    step = loopexpr.args[2]
                else:
                    step = Literal(1)
                fdef = ForStatement(target,lwb,upb,step,body)
                return [fdef]

        fdef = ForInStatement(target,loopexpr,body)
        return [fdef]

    def FunctionDef(self, ast):
        decorators = set()
        for decorator in ast.decorator_list:
            decorators.add(decorator.id)
        fname = ast.name
        argnames = []
        argdefaults = []

        for d in ast.args.defaults:
            argdefaults.append(self.visit(d))

        for a in ast.args.args:
            argnames.append(a.id)

        vararg = None
        kwarg = None
        if ast.args.vararg:
            vararg = ast.args.vararg
        if ast.args.kwarg:
            kwarg = ast.args.kwarg
        fdef = FunctionDefinitionStatement(fname)
        self.pushScope(fdef)
        body = self.Statements(ast.body)
        fdef.configure(decorators,argnames,argdefaults,vararg,kwarg,body)

        self.popScope()
        return [fdef]

    def Global(self, ast):
        globs = []
        for name in ast.names:
            globs.append(GlobalStatement(name))
            self.addGlobal(name)
        return globs

    def If(self,ast):
        tests = []
        cond = self.visit(ast.test)
        block = self.Statements(ast.body)
        tests.append((cond,block))
        elseblock = None
        if ast.orelse:
            elseblock = self.Statements(ast.orelse)
        idef = IfStatement(tests,elseblock)
        return [idef]

    def Import(self,ast):
        modules = []
        for name in ast.names:

            (modpath,namespace) = self.locateModule(name.name,name.asname)
            code = None

            mname = name.name
            if name.asname and name.asname !=  "":
                mname = name.asname
            self.module.addModuleMountPoint(mname,namespace)

            global loaded_modules
            if namespace not in loaded_modules:
                try:
                    code = pyread(modpath,(name.name,modpath,namespace,[]))
                except Exception, ex:
                    raise ex
                modules.append(code)
                loaded_modules.add(namespace)

        return modules

    def ImportFrom(self,ast):
        if ast.module == "__future__":
            return []

        importall = False
        if len(ast.names)==1 and ast.names[0].name=='*':
            importall = True
        namespace = self.module_namespace

        (modpath,namespace) = self.locateModule(ast.module,'')

        if importall == False:
            for name in ast.names:
                aliasedname = name.name
                if name.asname and name.asname != "":
                    aliasedname = name.asname

                unaliasedname = namespace + "." + name.name
                self.module.aliases.append((aliasedname,unaliasedname))
        else:
            namespace = self.module_namespace

        modules = []
        global loaded_modules
        if namespace not in loaded_modules:
            code = None
            try:
                code = pyread(modpath,(ast.module,modpath,namespace))
            except Exception, ex:
                # cannot find file, see if there is a "module equivalent"
                if importall:
                    for modname in pystorm_modules:
                        if ast.module.endswith(modname):
                            jspath = join("modules","javascript",pystorm_modules[modname]+".js")
                            jsfile = open(jspath,"r")
                            jscode = jsfile.read()
                            return [Verbatim(jscode)]
                raise ex
            modules.append(code)
            loaded_modules.add(namespace)
        return modules

    def locateModule(self,module,asname):
        modpath = module
        modpath = modpath.replace(".","/")
        modpath += ".py"
        (sourcedir,sourcefile) = split(self.module_path)
        modpath = join(sourcedir,modpath)
        namespace = ''

        # first see if the module is located relative to the calling module, but only
        # if the calling module is the initial module (or in the same directory)
        if sourcedir != initial_module_dir:
            try:
                testf = open(modpath,"r")
                ns = module
                if asname and asname !=  "":
                    ns = name.asname
                namespace = self.module_namespace
                if namespace.rfind(".") != -1:
                    namespace = namespace[:namespace.rfind(".")]
                if namespace != "":
                    namespace += "."
                namespace += ns
                return (modpath,namespace)
            except:
                pass

        # assume that the module is relative to the top level module
        # FIXME also search the current PYTHONPATH
        modpath = module
        modpath = modpath.replace(".","/")
        modpath += ".py"
        modpath = join(initial_module_dir,modpath)
        if asname and asname != "":
            namespace = asname
        else:
            namespace = module
        return (modpath,namespace)

    def Module(self,ast):
        m = Module(self.module_name,self.module_path,self.module_namespace)
        self.module = m
        self.pushScope(m)
        modulebody = self.Statements(ast.body)
        m.configure(modulebody)
        self.popScope()
        return m

    def Pass(self,ast):
        edef = EmptyStatement()
        return [edef]

    def Print(self,ast):
        pvalues = []
        for value in ast.values:
            pvalue = self.visit(value)
            pvalues.append(pvalue)
        pdef = PrintStatement(pvalues)
        return [pdef]

    def Raise(self, r):
        rtype = None
        robj = None
        if r.type:
            rtype = self.visit(r.type)
        if r.inst:
            robj = self.visit(r.inst)
        rdef = RaiseStatement(rtype,robj)
        return [rdef]

    def Return(self,ast):
        rvalue = self.visit(ast.value)
        rdef = ReturnStatement(rvalue)
        return [rdef]

    def Statements(self,ast):
        statements = []
        skip = False
        for s in ast:
            stmts = []
            try:
                stmts = self.visit(s)
            except:
                if not skip:
                    raise
                else:
                    stmts = []
            for stmt in stmts:
                if stmt:
                    if isinstance(stmt,ExpressionStatement):
                        expr = stmt.expr
                        if isinstance(expr,Literal):
                            val = expr.value
                            if isinstance(val,str):
                                if val.startswith('pystorm-verbatim:'):
                                    statements.append(Verbatim(val[len('pystorm-verbatim:'):]))
                                    continue
                                if val.startswith('pystorm-skip-begin'):
                                    skip = True
                                    continue
                                if val.startswith('pystorm-skip-end'):
                                    skip = False
                                    continue
                    if not skip:
                        statements.append(stmt)
        block = Block(statements)

        return block

    def TryFinally(self, ast):
        block = self.Statements(ast.body)
        handlers = []
        if isinstance(block,Block) and len(block.statements)==1:
            stmt = block.statements[0]
            if isinstance(stmt,TryStatement):
                block = stmt.body
                handlers = stmt.handlers
        finalblock = self.Statements(ast.finalbody)
        # fixme check for else
        tdef = TryStatement(block,handlers,finalblock)
        return [tdef]

    def TryExcept(self, ast):
        block = self.Statements(ast.body)
        handlers = []
        for h in ast.handlers:
                handlers.append(self.visit(h))
        # fixme check for else

        tdef = TryStatement(block,handlers,None)
        return [tdef]

    def ExceptHandler(self, ast):
        ast.body = self.Statements(ast.body)
        return ast

    def While(self, ast):
        cond = self.visit(ast.test)
        body = self.Statements(ast.body)
        wdef = WhileStatement(cond,body)
        return [wdef]

    def With(self,ast):
        raise FrontEndNotHandledException("with clause not supported",ast.lineno)

    def Yield(self,ast):
        raise FrontEndNotHandledException("yield clause not supported",ast.lineno)

def pyread(path,module=None):
    # print "// parsing:"+path
    if module == None:
        module = ("__main__",path,"")
        (mdir,mfile) = split(path)
        global initial_module_dir
        initial_module_dir = mdir
        global loaded_modules
        loaded_modules = set()
    file = codecs.open( path, "r", "utf-8" )
    contents = file.read()
    gv = GenVisitor(module[0],module[1],module[2])
    return gv.parse(contents)

