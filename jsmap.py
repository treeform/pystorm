# The MIT License
#
# Copyright (c) 2008 - 2009 Niall McCarroll
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# jsmap.py
#
# easy to use mapping from python to javascript operators and functions
#

# parameter substitution is controlled by using placeholders %1,%2,... in the mapped string
#
# if no placeholders are supplied, default substitution is carried out as:
#
# binary ops:
#   %1 <mapped-name> %2
#
# unary ops:
#   <mapped-name> %1
#
# function/method calls:
#   <mapped-name>(%1,%2,...,%N)

 
# map between python operators and javascript operators or functions
#
#

# binary operators

binaryOps = { 
    'and'       : '&&', 
    'or'        : '||', 
    '=='        : '==', 
    '!='        : '!=', 
    '**'        : 'Math.pow(%1,%2)',
    '[]'        : '%1[%2]',
    '<'         : '<',
    '<='        : '<=',
    '>'         : '>',
    '>='        : '>=',
    '<>'        : '!=',
    '!='        : '!=',
    'is'        : None,
    'is not'    : None,
    'in'        : ('__in(%1,%2)',['__in']),
    'not in'    : '!(%1 in %2)',
    '|'         : '|',
    '^'         : '^',
    '&'         : '&',
    '%'         : ('__mod_format(%1,%2)',['__mod_format']),
    '//'        : 'Math.floor(%1/%2)',
    '+'         : '+',
    '-'         : '-',
    '*'         : '*',
    '/'         : '/',
    '>>'        : '>>',
    '<<'        : '<<'
    }

# unary operators

unaryOps = { 
    'not'       : '!', 
    '-'         : '-',
    '+'         : '+',
    '~'         : '~'
}

# augmented assignment operators (always supply placeholders)

assignOps = {
    '+='        : '%1 += %2',
    '-='        : '%1 -= %2',
    '*='        : '%1 *= %2',
    '/='        : '%1 /= %2',
    '//='       : '%1 = Math.floor(%1/%2)',
    '%='        : '%1 %= %2',
    '>>='       : '%1 >>= %2',
    '<<='       : '%1 <<= %2',
    '**='       : '%1 = Math.pow(%1,%2)',
    '&='        : '%1 &= %2',
    '|='        : '%1 |= %2',
    '^='        : '%1 ^= %2'
}

#
# map between python builtins and javascript operators, functions or whatever
#
# where python and javascript builtin are the same, no need to include the mapping in this file
#
# for keys use the function name or "." plus the method name
# 
# to provide different mappings based on the number of arguments 
# supplied to the function/method, add the suffix .<#args> to the key.  
# 
# For example:
#   "spam.1" : js_eggs"   ... maps python function spam to javascript function js_eggs when exactly 
#                             1 argument is supplied   
#   "spam" : "js_spam"    ... maps python function spam to javascript function js_spam
#   

mappedFuncs = { 
# lists
    'len' : ('__len(%1)',['__len']), 
    '.append' : 'push',
    'sum' : ('__sum',['__sum']),
    'map' : ('__map',['__map']),
    'reduce' : ('__reduce',['__reduce']),
    'zip' : ('__zip',['__zip']),
    'filter' : ('__filter',['__filter']),
    'min' : ('__minmax(%1,true)',['__minmax']),
    'max' : ('__minmax(%1,false)',['__minmax']),
    '.sort.0' : 'sort',
    '.sort.1' : 'sort',
    '.sort.2' : ('__sort3(%0,%1,%2,false)',['__sort3']),
    '.sort.3' : ('__sort3(%0,%1,%2,%3)',['__sort3']),
    'xrange.2' : ( '__xrange2(%1,%2)',['__xrange2']),
    '.extend' : ( '__extend(%0,%1)', ['__extend']),
# conversion
    'str' : ('__str(%1)',['__str']),
    'int' : ('__int(%1)',['__int','ValueError']),
    'float' : ('__float(%1)',['__float','ValueError']),
# strings
    '.upper' : 'toUpperCase',
    '.lower' : 'toLowerCase',
    '.find' : 'indexOf',
    '.rfind' : 'lastIndexOf',
    '.splitlines.1' : None,
    '.splitlines.0' : 'split("\\n")',
    '.split.2' : None,
    '.split.1' : 'split(%1)',
    '.split.0' : 'split(/\s+/)',
    '.replace' : ('__replace(%0,%1,%2)',['__replace']),
    '.count' : ('__count(%0,%*)',['__count']),
    '.rstrip.0' : ('__rstrip(%0,"\\n\\t ")',['__rstrip']),
    '.rstrip.1' : ('__rstrip(%0,%1)',['__rstrip']),
    '.lstrip.0' : ('__lstrip(%0,"\\n\\t ")',['__lstrip']),
    '.lstrip.1' : ('__lstrip(%0,%1)',['__lstrip']),
    '.strip.0' : ('__rstrip(__lstrip(%0,"\\n\\t "),"\\n\\t ")',['__rstrip','__lstrip']),
    '.strip.1' : ('__rstrip(__lstrip(%0,%1),%1)',['__rstrip','__lstrip']),
#general
    'isinstance' : '%1 instanceof %2',
    '.keys' : ('__keys(%0)',['__keys']),
    '.has_key' : '(%1 in %0)',
    'super' : '%1.super(%2)'
}


