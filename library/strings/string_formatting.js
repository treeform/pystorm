
function py2js_next_token(str,start,match,incl,limit) {
    var pos = 0;
    var token = '';
    while(true) {
        if (start+pos > str.length) {
            return [null,(start+pos)];
        }
        var ch = str[start+pos];
        var contains = (match.indexOf(ch)==-1);
        var use = contains;
        if (!incl) {
            use = !contains;
        }
        if (use) {
            // print("token="+token);
            return [token,(start+pos)];
        } else {
            token += ch;
        }
        if ((limit > -1) && (token.length >= limit)) {
            return [token,(start+pos)];
        }
        pos++;
    }
    return null; 
}
        
                            
function py2js_parse_format(format,start) {
    var pos = start+1; // skip the %

    // initialize the return object
    var fmt = new Object();
    fmt.key = null;
    fmt.code = null;
    fmt.nbytes = 0;
    fmt.useplus = false;
    fmt.ljust = false;
    fmt.space_pad = false;
    fmt.zero_pad = false;
    fmt.alternate = false;

    fmt.width = null;
    fmt.precision = null;
    
    var ch = format[pos];
    
    // parse key (optional)   
    if (ch == '(') {
        [key,pos] = py2js_next_token(format,pos+1,")",false,-1);
        if (key == null) { return null; } 
        fmt.key = key;
        pos++; // skip the closing (
    }

    // flags
    var flags = '';
    [flags,pos] = py2js_next_token(format,pos,'+- 0#',true,-1);
    if (flags == null) { return null; }
    if (flags.indexOf('+') != -1) { fmt.useplus = true; }
    if (flags.indexOf('-') != -1) { fmt.ljust = true; }
    if (flags.indexOf(' ') != -1) { fmt.space_pad = true; }       
    if (flags.indexOf('0') != -1) { fmt.zero_pad = true; }
    if (flags.indexOf('#') != -1) { fmt.alternate = true; }
    if (flags.useplus) {
        flags.space_pad = false;
    }

    // width
    [wstr,pos] = py2js_next_token(format,pos,'0123456789*',true,-1);
    if (wstr == null) { return null; }
    if (wstr != '') { fmt.width = (wstr=='*') ? '*' : Number(wstr); }

    // precision
    if (pos >= format.length) { return null; }
    ch = format[pos];
    if (ch == '.') { 
        [pstr,pos] = py2js_next_token(format,pos+1,'0123456789*',true,-1);
        if (pstr == null) { return null; }
        if (pstr != '') { fmt.precision = (pstr=='*') ? '*' : Number(pstr); }
        if (pos >= format.length) { return null; }
        ch = format[pos];        
    }

    // length modifier (ignore this)
    [lstr,pos] = py2js_next_token(format,pos,"lh",true,-1);
    if (lstr == null) { return null; }
    if (pos >= format.length) { return null; }
    ch = format[pos];    

    // code
    if ("srcdiuoxXeEfFgG".indexOf(ch) == -1) { return null; }
    fmt.code = ch; 
    fmt.pos = pos;
    return fmt;
}

function py2js_apply_format(fmt,values,counter) {
    var width = -1;
    var precision = 6;

    if (fmt.width != null) {
        width = fmt.width;
        if (width == '*') { width = Number(values[counter++]); }
    }

    if (fmt.precision != null) {
        precision = fmt.precision;
        if (precision == '*') { precision = Number(values[counter++]); }
    }

    if (fmt.key != null) {
        val = values[fmt.key];
    } else {
        val = values[counter++];
    } 

    var result = null;
    var absval = null;
    var numeric = true;
    switch(fmt.code) {
        case 'r':
            numeric = false;
            if (val.__repr__) {
                result = val.__repr__();
                break;            
            }
        case 's': 
        case 'c':
            numeric = false;
            result = String(val); 
            break;
        case 'i':
        case 'u': 
        case 'd':
            absval = Math.abs(val);
            result = String(Math.floor(absval));
            break;
        case 'o':
            absval = Math.abs(val);
            result = '';
            if (fmt.alternate && val != 0) {
                result += '0';
            }
            result += absval.toString(8);
            break;
        case 'x':
        case 'X':
            absval = Math.abs(val);
            result = '';
            if (fmt.alternate) {
                result += '0x';
            }
            result += absval.toString(16);
            break;
        case 'f':
        case 'F':
        case 'g':
        case 'G':
            absval = Math.abs(val);
            var decimal_range = ((absval == 0) || (absval >= 0.0001 && absval < 1000000));
            if (!((fmt.code == 'g') || (fmt.code == 'G')) || decimal_range) { 
                if (fmt.code == 'g' || fmt.code == 'G') {
                    var integerval = Math.floor(absval);
                    var integerstr = integerval.toString();
                    // if (integerstr != "0") {
                        if (fmt.code == 'g' || fmt.code == 'G') {
                            precision = precision - integerstr.length;
                        }
                    // }
                    if (precision < 0 || ((absval - integerval) == 0) && !fmt.alternate) {
                        precision = 0;
                    }
                }
                result = absval.toFixed(precision);
                break;
            }
        case 'e':
        case 'E':
            absval = Math.abs(val);
            if (fmt.code == 'g' || fmt.code == 'G') {
                if (precision > 1) {
                    precision--;
                }
            }
            result = absval.toExponential(precision);
            var plus = result.indexOf('e')
            if (plus != -1) {
                var s = result.slice(plus+2);
                if (s.length == 1) {
                    result = result.slice(0,plus+2)+"0"+s;
                }
            }
            break;            
        default: 
            result = "?";
    }
    
    var signchar = null;
    if (numeric) {
        if (val < 0) {
            signchar = '-';
        } else if (fmt.useplus) { 
            signchar = '+';
        } else if (fmt.space_pad) { 
            signchar = " "; 
        }
    }

    if (fmt.code == 'X' || fmt.code == 'E' || fmt.code == 'G' || fmt.code == 'F') {
        result = result.toUpperCase();
    }

    var pad = ' ';
    if (fmt.zero_pad) {
        pad = '0';
    }

    if ((fmt.ljust || !fmt.zero_pad) && signchar) {
        result = signchar + result;
        signchar = null;    
    }

    if (width != -1) {
        w = result.length;
        if (signchar) {
            w = w + 1;
        }
        while(w < width) {
            if (fmt.ljust) {
                result = result + ' ';
            } else {
                result = pad + result;
            }
            w++;
        }
    }

    if (signchar) {
        result = signchar + result;
    }

    return [result,counter];
}    

function py2js_mod_format(a1,a2) {
    if (typeof(a1) == 'number') {
        return (a1 % a2);
    }    
    var mapping_format = false;
    var tystr = typeof(a2);
    if (tystr == 'string' || tystr == 'number' ) {
        a2 = [a2];       
    } else {
        if (!(a2 instanceof Array)) {
            mapping_format = true;
        } 
    }
    var result = '';
    var index = 0;
    var i = 0;
    var conv_counter = 0;
    while(i<a1.length) {
        if (a1[i] == '%') {
            if (i+1 == a1.length) {
                result += '%';
                i += 1;
            } 
            else if (a1[i+1] == '%') {
                result += '%';
                i += 2;
            }
            else {
                var fmt = py2js_parse_format(a1,i);
                i = fmt.pos;
                // print("nb="+String(fmt.nbytes));
                [s,conv_counter] = py2js_apply_format(fmt,a2,conv_counter);               
                result += s;
            }
        } else {
            result += a1[i];
        }
        i++;
    }
    return result;
}
