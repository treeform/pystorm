

function py2js_in(item,container) {
        if (container instanceof Array) {
            return container.indexOf(item) != -1;
        }
        return item in container;
}


// generated by py2js from tests/basic/dictionary.py


var __name__ = '__main__';


foo={'a':'b','c':'d'};
console.log(String((foo['a'])));
console.log(String((foo['c'])));
if (py2js_in('a',foo)) {
    console.log(String('a in foo'));
}