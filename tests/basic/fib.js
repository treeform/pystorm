// generated by py2js from tests/basic/fib.py


var __name__ = '__main__';

function fib(x)  {
    if (x == 1) {
        return x;
    }else  {
        return (x * fib((x - 1)));
    }
}
console.log(String(fib(4)));