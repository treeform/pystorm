"""
A library of javascript code to provide an equivalent to python built-in functions and methods
"""

pystorm_modules = { "mtrandom" : "MersenneTwister19937class" }

pystorm_lib = { 

"Kwarg":"""
function Kwarg(dict) {
    this.dict = dict;
}
Kwarg.prototype.getDict = function() {
    return this.dict;
}
""",

"__in":"""

function __in(item,container) {
        if (container instanceof Array) {
            return container.indexOf(item) != -1;
        }
        return item in container;
}
""",

"__len":"""

function __len(container) {
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
""",

"__xrange2":"""

function __xrange2(min,max) {
        result = [];
        var i;
        for(i=min;i<max;i++) {
            result.push(i);
        }
        return result;
}
""",

"__replace":"""
function __replace(str,mat,rep) {
    var s = str;    
    var pos = s.indexOf(mat,0);
    while(pos >= 0) {
        s = "".concat(s.slice(0,pos),rep,s.slice(pos+mat.length));
        pos = s.indexOf(mat,pos+rep.length);
    }
    return s;
}
""",

"__sort3":"""
function __sort3(lst,fn,ky,rv) {
    sfn = function(a,b) {
        if (!rv) {
            return fn(ky(a),ky(b));
        } else {
            return fn(ky(b),ky(a));
        }    
    }
    lst.sort(sfn);
}
""",

"__rstrip":"""
function __rstrip(str,chars) {
    var i = str.length-1;    
    while(i >= 0) {
        if (chars.indexOf(str.slice(i,i+1)) == -1) {
            break;
        }            
        i--;
    }
    if (i < (str.length-1)) {
        if (i < 0) {
            return "";
        }
        return str.slice(0,i+1);
    }
    return str;
}
""",

"__lstrip":"""
function __lstrip(str,chars) {
    var i = 0;    
    while(i < str.length) {
        if (chars.indexOf(str.slice(i,i+1)) == -1) {
            break;
        }            
        i++;
    }
    if (i == 0) {
        return str;
    }    
    if (i == str.length) {
        return "";
    }
    return str.slice(i);
}
""",

"__sum":"""
function __sum(list) {
    var i,total = 0;
    for(i=0;i<list.length;i++) {
        total += list[i];
    }    
    return total;
}
""",

"__extend":"""
function __extend(list1,list2) {
    var i;
    for(i=0;i<list2.length;i++) {
        list1.push(list2[i]);
    }    
}
""",

"__keys":"""
function __keys(obj) {
    var result = [];
    var k;
    for ( k in obj ) {
        result.push(k);
    }    
    return result;
}
""",

"__minmax":"""
function __minmax(list,minNotMax) {
    var result = null;
    /* FIXME should throw ValueError if list is empty */    
    for(i=0;i<list.length;i++) {
        if ((result == null) || (minNotMax && list[i]<result) || (!minNotMax && list[i]>result)) {
            result = list[i];
        }
    }    
    return result;
}
""",

"__map":"""
function __map(fn,list) {
    var i,result=[];
    for(i=0;i<list.length;i++) {
        result.push(fn(list[i]));
    }    
    return result;
}
""",

"__mod_format":"file:library/strings/string_formatting.js",

"__filter":"""
function __filter(fn,list) {
    var results = [];
    var i = 0;
    for(i=0; i<list.length; i++) {
        v = list[i];
        if (fn(v)) {
            results.push(v);
        }
    }
    return results;
}
""",

"__reduce":"""
function __reduce(fn,list) {
    var pos = 0;
    var result = null;
    if (arguments.length == 3) {
        result = arguments[2];
    }
    if (result == null) {
        pos = 1;
        result = list[0];    
    }

    for(i=pos;i<list.length;i++) {
        result = fn(result,list[i]);
    }    

    return result;
}
""",

"__zip":"""
function __zip() {
    
    if (arguments.length == 0) {
        return [];
    }

    var results = [];
    var pos = -1;
    var i = 0;
    var cont = true;
    while(cont) {
        pos++;
        for(i=0;i<arguments.length;i++) {
            if (pos >= arguments[i].length) {
                cont = false;
                break;
            }
        }
        if (cont) {
            var newitem = [];
            for(i=0; i<arguments.length;i++) {
               newitem.push(arguments[i][pos]);
            }
            results.push(newitem);
        }
    }
    return results;
}
""",

"__count":"""
function __count(str,sub,start,end) {
    var pos = 0;
    if (start != undefined) {
        if (start < 0) {
            start = str.length + start;
        }
        if (start < 0) {
            start = 0;
        }
        pos = start;
    }    
    if (end != undefined) {
        if (end < 0) {
            end = str.length + end;
        } 
        if (end < 0) {
            end = 0;
        }
    }
    pos = str.indexOf(sub,pos);
    var count = 0;
    while(pos >= 0) {
        if (end != undefined) {
            if (pos+sub.length > end) {
                break;
            }
        }
        count++;
        pos += sub.length;
        pos = str.indexOf(sub,pos);
    }
    return count;
}
""",

"Generator":"""


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


""",

"__int":"""

function __int(s) {
    if (typeof(s) == 'string' && s.indexOf('.') != -1) {
        throw(new ValueError("invalid literal for int: "+String(s)));
    }
    var n = new Number(s);
    if (isNaN(n)) {
        // warning text nicked from python ValueError
        throw(new ValueError("invalid literal for int: "+String(s)));
    }
    if (n < 0) {
        n = -Math.floor(Math.abs(n));
    } else {
        n = Math.floor(n);
    }        
    return n;
}

""",

"__float":"""

function __float(s) {
    var n = new Number(s);
    if (isNaN(n)) {
        // warning text nicked from python ValueError
        throw(new ValueError("invalid literal for float: "+String(s)));
    }
    return n;
}
""",

"__str":"""

function __str(v) {
    if (v && v.toFixed) {
        if (Math.floor(v) != v) {
            return v.toFixed(12);
        }
    }
    return new String(v);
}
""",

"ValueError":"""

function ValueError(details) {
    this.details = details;
    return this;
}
""" }


