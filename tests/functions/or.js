


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




// generated by py2js from tests/functions/or.py


var __name__ = '__main__';


tests=[[false,false],[false,true],[true,false],[true,true],[true,null],[false,null],[null,true],[null,false]];
function pp(v)  {
    if (v == false) {
        return 'F';
    }
    if (v == true) {
        return 'T';
    }
    return '?';
}


container_py2js_1=tests;
var generator_py2js_2 = new Generator(container_py2js_1);
for(t=generator_py2js_2.nextValue();generator_py2js_2.hadMore();t=generator_py2js_2.nextValue()) {
    
    [b1,b2]=t;
    console.log(String(((((pp(b1) + ' OR ') + pp(b2)) + '=') + pp((b1 || b2)))));
}
