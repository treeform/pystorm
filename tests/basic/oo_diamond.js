// generated by py2js from tests/basic/oo_diamond.py


var __name__ = '__main__';



function foobar()  {
    
    if (arguments.length==1 && arguments[0] == undefined) { return; }
    
    var self = new foobar(undefined);
    
    self.m4 = function() { return foobar.m4(this); }
    
    self.m1 = function() { return foobar.m1(this); }
    
    self.m3 = function() { return foobar.m3(this); }
    
    self.m2 = function() { return foobar.m2(this); }
    
    return self;
}

foobar.m4 = function(self)  {
    console.log(String('foobar.m4'));
}
foobar.m1 = function(self)  {
    console.log(String('foobar.m1'));
}
foobar.m3 = function(self)  {
    console.log(String('foobar.m3'));
}
foobar.m2 = function(self)  {
    console.log(String('foobar.m2'));
}
foobar.super = function(self) {
    this.self = self;
    return this;
}



function foo()  {
    
    if (arguments.length==1 && arguments[0] == undefined) { return; }
    
    var self = new foo(undefined);
    
    self.m4 = function() { return foo.m4(this); }
    
    self.m1 = function() { return foobar.m1(this); }
    
    self.m3 = function() { return foobar.m3(this); }
    
    self.m2 = function() { return foo.m2(this); }
    
    return self;
}

foo.m4 = function(self)  {
    console.log(String('foo.m4'));
}
foo.m2 = function(self)  {
    console.log(String('foo.m2'));
}
foo.super = function(self) {
    this.self = self;
    this.m4 = function() { return foobar.m4(this.self); }
    this.m1 = function() { return foobar.m1(this.self); }
    this.m3 = function() { return foobar.m3(this.self); }
    this.m2 = function() { return foobar.m2(this.self); }
    return this;
}



function bar()  {
    
    if (arguments.length==1 && arguments[0] == undefined) { return; }
    
    var self = new bar(undefined);
    
    self.m4 = function() { return foobar.m4(this); }
    
    self.m1 = function() { return foobar.m1(this); }
    
    self.m3 = function() { return bar.m3(this); }
    
    self.m2 = function() { return foobar.m2(this); }
    
    return self;
}

bar.m3 = function(self)  {
    console.log(String('bar.m3'));
}
bar.super = function(self) {
    this.self = self;
    this.m4 = function() { return foobar.m4(this.self); }
    this.m1 = function() { return foobar.m1(this.self); }
    this.m3 = function() { return foobar.m3(this.self); }
    this.m2 = function() { return foobar.m2(this.self); }
    return this;
}



function myfb()  {
    
    if (arguments.length==1 && arguments[0] == undefined) { return; }
    
    var self = new myfb(undefined);
    
    self.m4 = function() { return myfb.m4(this); }
    
    self.m1 = function() { return foobar.m1(this); }
    
    self.m3 = function() { return bar.m3(this); }
    
    self.m2 = function() { return foo.m2(this); }
    
    return self;
}

myfb.m4 = function(self)  {
    console.log(String('myfb.m4'));
}
myfb.super = function(self) {
    this.self = self;
    this.m4 = function() { return foo.m4(this.self); }
    this.m1 = function() { return foobar.m1(this.self); }
    this.m3 = function() { return bar.m3(this.self); }
    this.m2 = function() { return foo.m2(this.self); }
    return this;
}


x=myfb();
x.m1();
x.m2();
x.m3();
x.m4();
