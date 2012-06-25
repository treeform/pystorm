// generated by py2js from tests/modules/classname.py


var __name__ = '__main__';

// generated by py2js from tests/modules/modules/moda.py


__name__ = 'modules.moda';


// __main__->modules.moda
var modules = {};
modules.moda = {};


modules.moda.ModA = function(val)  {
    
    if (arguments.length==1 && arguments[0] == undefined) { return; }
    
    var self = new modules.moda.ModA(undefined);
    
    self.clone = function() { return modules.moda.ModA.clone(this); }
    
    self.describe = function() { return modules.moda.ModA.describe(this); }
    
    modules.moda.ModA.__init__(self,val);
    
    return self;
}

modules.moda.ModA.__init__ = function(self,val)  {
    self.val=val;
}
modules.moda.ModA.clone = function(self)  {
    return modules.moda.ModA(self.val);
}
modules.moda.ModA.describe = function(self)  {
    console.log(String(self.val));
}
modules.moda.ModA.super = function(self) {
    this.self = self;
    return this;
}




__name__ = '__main__';



m=modules.moda.ModA('hello');
m.describe();

mc=m.clone();
mc.describe();
