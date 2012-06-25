
function py2js_rstrip(str,chars) {
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


// generated by py2js from tests/strings/rstrip1.py


var __name__ = '__main__';


s='abcxyz';
console.log(String((('original(' + s) + ')')));
console.log(String((('strip(' + py2js_rstrip(s,'yzx')) + ')')));
