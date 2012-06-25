


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




// generated by py2js from tests/strings/split.py


var __name__ = '__main__';


s='the     quick brown fox jumped over the lazy dog';

t=s.split(' ');


container_py2js_1=t;
var generator_py2js_2 = new Generator(container_py2js_1);
for(v=generator_py2js_2.nextValue();generator_py2js_2.hadMore();v=generator_py2js_2.nextValue()) {
    console.log(String(v));
}

r=s.split('e');


container_py2js_3=r;
var generator_py2js_4 = new Generator(container_py2js_3);
for(v=generator_py2js_4.nextValue();generator_py2js_4.hadMore();v=generator_py2js_4.nextValue()) {
    console.log(String(v));
}

x=s.split(/\s+/);


container_py2js_5=x;
var generator_py2js_6 = new Generator(container_py2js_5);
for(v=generator_py2js_6.nextValue();generator_py2js_6.hadMore();v=generator_py2js_6.nextValue()) {
    console.log(String(v));
}