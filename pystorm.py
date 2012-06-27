# read a python file and attempt to convert to javascript
#
# usage:
#
#   python pystorm.py example.py > example.js
#
#   python pystorm.py example.py -debug > example.js
#       (convert and embed a comment in the output with the parsetree, for debugging purposes)

from pyfrontend import pyread, FrontendException
from jsbackend import jswrite, BackendException
import sys


argfile = sys.argv[1]
debug = False
if len(sys.argv)>2:
    if sys.argv[2] == '-debug':
        debug = True

code = None
try:
    code = pyread(argfile)
except FrontendException, ex:
    print "Frontend Error: " + str(ex)

if debug:
    print "/* " + str(code) + " */"

if code:
    try:
        print jswrite(code,argfile)
    except BackendException, ex:
        print "Backend Error: " + str(ex)

