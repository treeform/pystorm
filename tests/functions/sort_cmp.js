// generated by py2js from tests/functions/sort_cmp.py


var __name__ = '__main__';

function revcmp(a,b)  {
    if (b < a) {
        return -1;
    }
    if (b == a) {
        return 0;
    }
    return 1;
}

l=[4,7,2,3,8,1,3];
l.sort(revcmp);
console.log(String((l[0])));
console.log(String((l[1])));
console.log(String((l[2])));