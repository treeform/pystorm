
function py2js_keys(obj) {
    var result = [];
    var k;
    for ( k in obj ) {
        result.push(k);
    }    
    return result;
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




// generated by py2js from tests/basic/keys.py


var __name__ = '__main__';


x={'foo':'bar','aaa':'bbb','xyz':'zyx','spam':'eggs'};

s=py2js_keys(x);
s.sort();


container_py2js_1=s;
var generator_py2js_2 = new Generator(container_py2js_1);
for(k=generator_py2js_2.nextValue();generator_py2js_2.hadMore();k=generator_py2js_2.nextValue()) {
    console.log(String(((k + ' -> ') + (x[k]))));
}