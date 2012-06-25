


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




// generated by py2js from tests/basic/listcomp2.py


var __name__ = '__main__';



var comp_py2js_2= [];
 {
    
    for(x=0;x<3;x+=1) {
        
        for(y=0;y<4;y+=1) {
            
            for(z=0;z<5;z+=1) {
                comp_py2js_2.push([x,y,z]);
            }
        }
    }
}container_py2js_1=comp_py2js_2;
var generator_py2js_3 = new Generator(container_py2js_1);
for(loop_py2js_4=generator_py2js_3.nextValue();generator_py2js_3.hadMore();loop_py2js_4=generator_py2js_3.nextValue()) {
    [x,y,z]=loop_py2js_4;
    if ((x < y) && (y < z)) {
        console.log(String(x)+ " " +String(y)+ " " +String(z)+ " " +String('x<y<z'));
    }
}