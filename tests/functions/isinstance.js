// generated by py2js from tests/functions/isinstance.py


var __name__ = '__main__';



function Spam(value)  {
    
    if (arguments.length==1 && arguments[0] == undefined) { return; }
    
    var self = new Spam(undefined);
    
    Spam.__init__(self,value);
    
    return self;
}

Spam.__init__ = function(self,value)  {
    self.value=value;
}
Spam.super = function(self) {
    this.self = self;
    return this;
}



function Eggs(value)  {
    
    if (arguments.length==1 && arguments[0] == undefined) { return; }
    
    var self = new Eggs(undefined);
    
    Eggs.__init__(self,value);
    
    return self;
}

Eggs.__init__ = function(self,value)  {
    self.value=value;
}
Eggs.super = function(self) {
    this.self = self;
    return this;
}


s=Spam(1);

e=Eggs(2);
if (s instanceof Spam) {
    console.log(String('s is Spam - correct'));
}
if (s instanceof Eggs) {
    console.log(String('s is Eggs - incorrect'));
}
if (e instanceof Spam) {
    console.log(String('e is Spam - incorrect'));
}
if (e instanceof Eggs) {
    console.log(String('e is Eggs - correct'));
}