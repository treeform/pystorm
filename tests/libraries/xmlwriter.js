

function py2js_len(container) {
        if (container instanceof Array) {
            return container.length;
        }
        var i;
        var count = 0;
        for (i in container) {
            count++;
        }
        return count;
}





function Generator(container) {
        var isarray = (container instanceof Array);
        var isstring = (typeof(container) == 'string');
        if (container.__iter__) {
                this.values = [];
                this.iterator = container.__iter__();
        } else if (isarray || isstring) {
                this.values = container;
        } else {
                this.values = [];
                for(key in container) {
                        this.values.push(key);
                }
        }
        this.index = 0;
}

Generator.prototype.nextValue = function() {
        if (this.iterator) {
                try {
                        return this.iterator.next();
                } catch( e ) {
                        this.iterator_exhausted = true;
                        return null;
                }
        }
        else if (this.index < this.values.length) {
                return this.values[this.index++];
        } else {
                this.index++;
                return null;
        }
}

Generator.prototype.hadMore = function() {
        if (this.iterator_exhausted) {
                return false;
        }
        return (this.index-1) < this.values.length;
}




// generated by py2js from tests/libraries/xmlwriter.py


var __name__ = '__main__';



function StringWriter()  {
    
    if (arguments.length==1 && arguments[0] == undefined) { return; }
    
    var self = new StringWriter(undefined);
    
    self.write = function(text) { return StringWriter.write(this,text); }
    
    self.getContents = function() { return StringWriter.getContents(this); }
    
    StringWriter.__init__(self);
    
    return self;
}

StringWriter.__init__ = function(self)  {
    self.contents='';
}
StringWriter.write = function(self,text)  {
    self.contents += text;
}
StringWriter.getContents = function(self)  {
    return self.contents;
}
StringWriter.super = function(self) {
    this.self = self;
    return this;
}



function XmlWriter()  {
    
    if (arguments.length==1 && arguments[0] == undefined) { return; }
    
    var self = new XmlWriter(undefined);
    
    self.write = function(writer) { return XmlWriter.write(this,writer); }
    
    self.indent = function(writerindent) { return XmlWriter.indent(writerindent); }
    
    self.createRoot = function(tag) { return XmlWriter.createRoot(this,tag); }
    
    self.Node=XmlWriter.Node;
    
    self.TextNode=XmlWriter.TextNode;
    
    self.Element=XmlWriter.Element;
    
    return self;
}

XmlWriter.write = function(self,writer)  {
    self.root.write(writer,0);
}
XmlWriter.indent = function(writer,indent)  {
    writer.write('\n');
    var x;
    for(x=0;x<indent;x+=1) {
        writer.write('  ');
    }
}
XmlWriter.createRoot = function(self,tag)  {
    self.root=self.Element(tag);
    return self.root;
}
XmlWriter.super = function(self) {
    this.self = self;
    return this;
}



XmlWriter.Node = function()  {
    
    if (arguments.length==1 && arguments[0] == undefined) { return; }
    
    var self = new XmlWriter.Node(undefined);
    
    XmlWriter.Node.__init__(self);
    
    return self;
}

XmlWriter.Node.__init__ = function(self)  {
    /* pass */
}
XmlWriter.Node.super = function(self) {
    this.self = self;
    return this;
}



XmlWriter.TextNode = function(text)  {
    
    if (arguments.length==1 && arguments[0] == undefined) { return; }
    
    var self = new XmlWriter.TextNode(undefined);
    
    self.write = function(writer,indent) { return XmlWriter.TextNode.write(this,writer,indent); }
    
    XmlWriter.TextNode.__init__(self,text);
    
    return self;
}

XmlWriter.TextNode.__init__ = function(self,text)  {
    self.text=text;
}
XmlWriter.TextNode.write = function(self,writer,indent)  {
    writer.write(self.text);
}
XmlWriter.TextNode.super = function(self) {
    this.self = self;
    this.__init__ = function() { return XmlWriter.Node.__init__(this.self); }
    return this;
}



XmlWriter.Element = function(tag)  {
    
    if (arguments.length==1 && arguments[0] == undefined) { return; }
    
    var self = new XmlWriter.Element(undefined);
    
    self.write = function(writer,indent) { return XmlWriter.Element.write(this,writer,indent); }
    
    self.addTextNode = function(text) { return XmlWriter.Element.addTextNode(this,text); }
    
    self.addElement = function(tag) { return XmlWriter.Element.addElement(this,tag); }
    
    self.__init__ = function() { return XmlWriter.Node.__init__(this); }
    
    self.addAttribute = function(name,value) { return XmlWriter.Element.addAttribute(this,name,value); }
    
    XmlWriter.Element.__init__(self,tag);
    
    return self;
}

XmlWriter.Element.__init__ = function(self,tag)  {
    self.tag=tag;
    self.children=[];
    self.attributes={};
    self.hastext=false;
}
XmlWriter.Element.write = function(self,writer,indent)  {
    if (indent > 0) {
        XmlWriter.indent(writer,indent);
    }
    writer.write(('<' + self.tag));
    var k;
    var container_py2js_1;
    container_py2js_1=self.attributes;
    var generator_py2js_2 = new Generator(container_py2js_1);
    for(k=generator_py2js_2.nextValue();generator_py2js_2.hadMore();k=generator_py2js_2.nextValue()) {
        writer.write(((((' ' + k) + '="') + (self.attributes[k])) + '"'));
    }
    if (py2js_len(self.children) == 0) {
        writer.write(' />');
        return;
    }
    writer.write('>');
    var c;
    var container_py2js_3;
    container_py2js_3=self.children;
    var generator_py2js_4 = new Generator(container_py2js_3);
    for(c=generator_py2js_4.nextValue();generator_py2js_4.hadMore();c=generator_py2js_4.nextValue()) {
        c.write(writer,(indent + 1));
    }
    if (! self.hastext) {
        XmlWriter.indent(writer,indent);
    }
    writer.write((('</' + self.tag) + '>'));
}
XmlWriter.Element.addTextNode = function(self,text)  {
    var child;
    child=XmlWriter.TextNode(text);
    self.children.push(child);
    self.hastext=true;
    return child;
}
XmlWriter.Element.addElement = function(self,tag)  {
    var child;
    child=XmlWriter.Element(tag);
    self.children.push(child);
    return child;
}
XmlWriter.Element.addAttribute = function(self,name,value)  {
    var self,name;
    (self.attributes[name])=value;
}
XmlWriter.Element.super = function(self) {
    this.self = self;
    this.__init__ = function() { return XmlWriter.Node.__init__(this.self); }
    return this;
}

if (__name__ == '__main__') {
    
    w=XmlWriter();
    
    r=w.createRoot('foo');
    
    r1=r.addElement('r1');
    r1.addAttribute('spam','eggs');
    
    r2=r1.addElement('r2');
    r2.addAttribute('eggs','spam');
    r2.addTextNode('This is some text');
    
    s=StringWriter();
    w.write(s);
    console.log(String(s.getContents()));
}
