// generated by py2js from tests/basic/closure.py


var __name__ = '__main__';

function factory(x)  {
    function fn()  {
        return x;
    }
    return fn;
}

a1=factory('foo');

a2=factory('bar');
console.log(String(a1()));
console.log(String(a2()));