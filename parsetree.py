# The MIT License
#
# Copyright (c) 2008 - 2009 Niall McCarroll
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# parsetree.py
#
# classes to model a parse tree that is a simplified equivalent to python's ast
#

# Expression related

class Expr(object):

    def __init__(self):
        pass

    def walk(self,walker):
        walker.begin(self)
        walker.end(self)

# Sub-classes of Expr
    
class AttributeLookup(Expr):

    def __init__(self,obj,attr):
        self.obj = obj
        self.attr = attr
        Expr.__init__(self)

    def __repr__(self):
        return str(('attribute',self.obj,self.attr))

    def walk(self,walker):
        walker.begin(self)
        self.obj.walk(walker)
        walker.end(self)

class BinaryOp(Expr):

    def __init__(self,op,left,right):
        self.op = op
        self.left = left
        self.right = right
        Expr.__init__(self)

    def __repr__(self):
        return str(('binaryop',self.op,self.left,self.right))

    def walk(self,walker):
        walker.begin(self)
        self.left.walk(walker)
        self.right.walk(walker)
        walker.end(self)

class DictionaryValue(Expr):

    def __init__(self,keyvalues):
        self.keyvalues = keyvalues
        Expr.__init__(self)

    def __repr__(self):
        return str(('keyvalues',self.keyvalues))

    def walk(self,walker):
        walker.begin(self)
        for (k,v) in self.keyvalues:
            if k:
                k.walk(walker)
            if v:
                v.walk(walker)
        walker.end(self)

class FunctionCall(Expr):

    def __init__(self,fname,args,kwargs):
        self.fname = fname
        self.args = args
        self.kwargs = kwargs
        Expr.__init__(self)

    def __repr__(self):
        return str(('fcall',self.fname,self.args,self.kwargs))

    def walk(self,walker):
        walker.begin(self)
        for arg in self.args:
            arg.walk(walker)
        # fixme kwargs?
        walker.end(self)

class Lambda(Expr):

    def __init__(self,args,body):
        self.args = args
        self.body = body
        Expr.__init__(self)

    def __repr__(self):
        return str(('lambda',self.args,self.body))

    def walk(self,walker):
        walker.begin(self)
        for arg in self.args:
            arg.walk(walker)
        self.body.walk(walker)
        walker.end(self)

class ListValue(Expr):

    def __init__(self,elements):
        self.elements = elements
        Expr.__init__(self)

    def __repr__(self):
        return str(('listvalue',self.elements))

    def walk(self,walker):
        walker.begin(self)
        for elt in self.elements:
            elt.walk(walker)
        walker.end(self)

class ListComprehension(Expr):

    def __init__(self,expr,generators):
        self.expr = expr
        self.generators = generators
        Expr.__init__(self)

    def __repr__(self):
        return str(('listcomp',self.expr,self.generators))

    def walk(self,walker):
        walker.begin(self)
        self.expr.walk(walker)
        for generator in self.generators:
            generator.walk(walker)
        walker.end(self)

class ListComprehensionGenerator(Expr):

    def __init__(self,target,itr,cond):
        self.target = target
        self.itr = itr
        self.cond = cond
        Expr.__init__(self)

    def __repr__(self):
        return str(('listcomp_gen',self.target,self.itr,self.conds))

    def walk(self,walker):
        walker.begin(self)
        self.target.walk(walker)
        self.itr.walk(walker)
        for generator in self.conds:
            generator.walk(walker)
        walker.end(self)

class Literal(Expr):

    def __init__(self,value):
        self.value = value
        Expr.__init__(self)

    def __repr__(self):
        return str(('literal',self.value))

class MethodCall(FunctionCall):

    def __init__(self,target,fname,args,kwargs):
        self.target = target
        FunctionCall.__init__(self,fname,args,kwargs)

    def __repr__(self):
        return str(('mcall',self.target,FunctionCall.__repr__(self)))

    def walk(self,walker):
        walker.begin(self)
        self.target.walk(walker)
        for arg in self.args:
            arg.walk(walker)
        walker.end(self)

class SliceOp(Expr):
    
    def __init__(self,target,slicing):
        self.target = target
        self.lwb = slicing[0]
        self.upb = slicing[1]
        self.step = slicing[2]

    def __repr__(self):
        return str(('slice',self.lwb,self.upb,self.step))

    def walk(self,walker):
        if self.lwb:
            self.lwb.walk(walker)
        if self.upb:
            self.upb.walk(walker)
        if self.step:
            self.step.walk(walker)
        walker.end(self)

class UniOp(Expr):

    def __init__(self,op,arg):
        self.op = op
        self.arg = arg
        Expr.__init__(self)

    def __repr__(self):
        return str(('unaryop',self.op,self.arg))

    def walk(self,walker):
        walker.begin(self)
        self.arg.walk(walker)
        walker.end(self)

class VarName(Expr):

    def __init__(self,varname):
        self.varname = varname
        Expr.__init__(self)

    def __repr__(self):
        return str(('var',self.varname))

    def __repr__(self):
        return str(('name',self.varname))

    def walk(self,walker):
        walker.begin(self)
        walker.end(self)

# Statement related


class Scope(object):

    def __init__(self,name):
        self.scopename = name
        self.globals = set()

    def addGlobal(self,name):
        self.globals.add(name)

    def isGlobal(self,name):
        return name in self.globals

    def printscope(self):
        return ('scope',self.scopename,self.locals,self.globals)
            
class Statement(object):

    def __init__(self):
        pass

# Statement sub-classes
       
class AssignmentStatement(Statement):
    
    def __init__(self,target,expr):
        self.target = target
        self.expr = expr
        Statement.__init__(self)

    def __repr__(self):
        return str(('assign',self.target,self.expr))

class AugmentedAssignmentStatement(Statement):
    
    def __init__(self,target,op,expr):
        self.target = target
        self.op = op
        self.expr = expr
        Statement.__init__(self)

    def __repr__(self):
        return str(('augmented_assign',self.varname,self.op,self.expr))

class BreakStatement(Statement):
    
    def __init__(self):
        Statement.__init__(self)

    def __repr__(self):
        return str(('break'))

class ClassDefinitionStatement(Statement,Scope):

    registered = {}

    def __init__(self,cname,module):
        self.cname = cname
        self.module = module
        self.parent_class = None
        Statement.__init__(self)
        Scope.__init__(self,"class:"+cname)

    def configure(self,bases,constructor,memberfns,staticvars,innerclasses):
        self.bases = bases
        self.constructor = constructor
        self.mfns = memberfns
        self.staticmembervars = staticvars
        self.innerclasses = innerclasses
        ClassDefinitionStatement.register(self)

    def getClassNamespace(self):
        if self.parent_class:
            namespace = self.parent_class.getClassNamespace()
        elif self.module:
            namespace = self.module.namespace
        else:
            namespace = ""
        if namespace != "":
            namespace += "."
        namespace += self.cname
        return namespace

    def setParentClass(self,parent):
        self.parent_class = parent

    def __repr__(self):
        return str(('cdef',self.cname,self.class_namespace,self.constructor,self.mfns,self.staticmembervars))

    @staticmethod 
    def register(cdef):
        ClassDefinitionStatement.registered[cdef.cname] = cdef

    @staticmethod
    def isclassname(name):
        return name in ClassDefinitionStatement.registered

    @staticmethod
    def getclass(name):
        if name in ClassDefinitionStatement.registered:
            return ClassDefinitionStatement.registered[name]
        else:
            return None

    # method resolution order utilities

    @staticmethod
    def getbases(C):
        klass = ClassDefinitionStatement.getclass(C)
        if klass != None:
            return klass.bases[:]
        else:
            return []

    # methods merge,mro and compute_mro based on code and description
    # of the method resolution order here:
    # http://www.python.org/download/releases/2.3/mro/
    @staticmethod
    def merge(seqs):
        res = []; i=0
        while 1:
          nonemptyseqs=[seq for seq in seqs if seq]
          if not nonemptyseqs: return res
          i+=1 
          for seq in nonemptyseqs: # find merge candidates among seq heads
              cand = seq[0] 
              nothead=[s for s in nonemptyseqs if cand in s[1:]]
              if nothead: cand=None #reject candidate
              else: break
          if not cand: raise "Inconsistent hierarchy"
          res.append(cand)
          for seq in nonemptyseqs: # remove cand
              if seq[0] == cand: del seq[0]

    @staticmethod
    def mro(C):
        "Compute the class precedence list (mro) according to C3"
        return ClassDefinitionStatement.merge([[C]]
                +map(ClassDefinitionStatement.mro,ClassDefinitionStatement.getbases(C))
                +[list(ClassDefinitionStatement.getbases(C))])

    @staticmethod
    def compute_mro(cname):
        namelist = ClassDefinitionStatement.mro(cname)
        return map(ClassDefinitionStatement.getclass,namelist)

    def memberfns(self,forsuper=False):
        classes = ClassDefinitionStatement.compute_mro(self.cname)
        fns = {}
        for clas in classes:
            # clas may be None for the base class (object or other built in class)
            if clas:
                cname = clas.cname
                if forsuper and cname == self.cname:
                    continue
                cfns = clas.mfns
                if forsuper and clas.constructor:
                    cfns.append(clas.constructor)
                for f in cfns:
                    fname = f.fname
                    if fname not in fns:
                        fns[fname] = (clas.getClassNamespace(),f)
                
        return fns

    def innerclasslist(self):
        classes = ClassDefinitionStatement.compute_mro(self.cname)
        innerclasses = []
        for clas in classes:
            if clas:
                for innerclass in clas.innerclasses:
                    innerclasses.append((innerclass,clas.getClassNamespace()))
        return innerclasses

class ContinueStatement(Statement):
    
    def __init__(self):
        Statement.__init__(self)

    def __repr__(self):
        return str(('continue'))

class DeleteStatement(Statement):

    def __init__(self,target):
        Statement.__init__(self)
        self.target = target

    def __repr__(self):
        return str(("delete",self.target))

class DeclareStatement(Statement):

    def __init__(self,declarevars):
        self.declarevars = declarevars
        Statement.__init__(self)

    def __repr__(self):
        return str(('declare',self.declarevars))        

class EmptyStatement(Statement):
    
    def __init__(self):
        Statement.__init__(self)

    def __repr__(self):
        return str(('pass'))

class ExceptionHandlerStatement(Statement):

    def __init__(self,etype,ename,ebody):
        self.etype = etype
        self.ename = ename
        self.ebody = ebody
        
    def __repr__(self):
        return str(('except',self.etype,self.ename,self.ebody))
  
class ExpressionStatement(Statement):

    def __init__(self,expr):
        self.expr = expr
        Statement.__init__(self)

    def __repr__(self):
        return str(('expression',self.expr))

class ForInStatement(Statement):
    
    def __init__(self,target,container,block):
        self.target = target
        self.container = container
        self.block = block
        Statement.__init__(self)

    def __repr__(self):
        return str(('for in',self.target,self.container,self.block))

class ForStatement(Statement):
    
    def __init__(self,varname,lwb,upb,step,block):
        self.varname = varname
        self.lwb = lwb
        self.upb = upb
        self.step = step
        self.block = block
        Statement.__init__(self)

    def __repr__(self):
        return str(('for',self.varname,self.lwb,self.upb,self.step,self.block))

class FunctionDefinitionStatement(Statement,Scope):

    def __init__(self,fname):
        self.fname = fname
        Statement.__init__(self)
        Scope.__init__(self,"function:"+fname)

    def configure(self,decorators,argnames,argdefaults,vararg,kwarg,block):
        self.decorators = decorators
        self.argnames = argnames
        self.argdefaults = argdefaults
        self.vararg = vararg
        self.kwarg = kwarg
        self.block = block

    def __repr__(self):
        return str(('fdef',self.fname,self.decorators,self.argnames,self.argdefaults,self.block))

class GlobalStatement(Statement):

    def __init__(self,varname):
        self.varname = varname
        Statement.__init__(self)

    def __repr__(self):
        return str(('global',self.varname))
        
class IfStatement(Statement):
    
    def __init__(self,tests,elseblock):
        self.tests = tests
        self.elseblock = elseblock
        Statement.__init__(self)

    def __repr__(self):
        return str(('if',self.tests,self.elseblock))

class PrintStatement(Statement):
    
    def __init__(self,values):
        self.values = values

    def __repr__(self):
        return str(('print',self.values))

class RaiseStatement(Statement):

    def __init__(self,rtype,robj):
        self.rtype = rtype
        self.robj = robj

    def __repr__(self):
        return str(('raise',self.rtype,self.robj))

class ReturnStatement(Statement):
    
    def __init__(self,returnvalue):
        self.value = returnvalue # may be None

    def __repr__(self):
        return str(('return',self.value))
    
class TryStatement(Statement):

    def __init__(self,body,handlers,final):
        self.body = body
        self.handlers = handlers
        self.final = final

    def __repr__(self):
        return str(('try',self.body,self.handlers,self.final))

class Verbatim(Statement):

    def __init__(self,text):
        self.text = text
        Statement.__init__(self)

    def __repr__(self):
        return str(('verbatim',self.text))

class WhileStatement(Statement):

    def __init__(self,cond,block):
        self.cond = cond
        self.block = block
        Statement.__init__(self)

    def __repr__(self):
        return str(('while',self.cond,self.block))

# Block contains a group of statements

class Block(object):

    def __init__(self,statements):
        self.statements = statements

    def __repr__(self):
        return str(('block',self.statements))

# Module describes a python module

class Module(Scope):

    def __init__(self,name,path,namespace):
        self.name = name
        self.path = path
        self.namespace = namespace
        self.module_mountpoints = {}
        self.class_mountpoints = {}
        self.aliases = []
        Scope.__init__(self,"module:"+self.name)

    def configure(self,code):
        self.code = code
        self.parent_module = None

    def setParentModule(self,parent_module):
        self.parent_module = parent_module

    def addModuleMountPoint(self,name,mountpoint):
        self.module_mountpoints[name] = mountpoint

    def addClassMountPoint(self,name,mountpoint):
        self.class_mountpoints[name] = mountpoint

    def getMountPoint(self,name):
        if name in self.module_mountpoints:
            return self.module_mountpoints[name]
        if name in self.class_mountpoints:
            return self.class_mountpoints[name]
        return None

    def getClassMountPoint(self,name):
        if name in self.class_mountpoints:
            return self.class_mountpoints[name]
        return None

    def applyAliases(self,name):
        for (originalname,namealias) in self.aliases:
           if name == originalname:
               return namealias
        return name

    def __repr__(self):
        return str(('module',self.name,self.aliases,self.code))

# Walker utilities

class VarNameWalker(object):

    def __init__(self):
        self.varnames = []

    def getVarNames(self):
        return self.varnames

    def begin(self,node):
        if isinstance(node,VarName):
            self.varnames.append(node.varname)
    
    def end(self,node):
        pass

# Scope utilities

def printscope(scope):
    for s in scope:
        print(str(s))

