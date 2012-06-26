
# Rational

Maybe I am just tired of coffee script compiler. Maybe python is a better platform then node. Maybe I am just spoild being able to run same code on the client as on the server. I just want coffee script to be python. I make it happen.

Python to javascript landsape is graveyard unfinished compilers. Why not take a compiler thats simple and have a good number of tests and try to breathe some life into it. This is what I have done with Niall McCarroll compiler.

# Running

python pystorm.py file.py > file.js

# Hacking

Files:
    * *pystrom.py* - main 
    * *pyfrontend.py* - this file reads the python's ast and transforms it a little bit into parsetree's classes.
    * *jsbackend.py* - this is the backend part, takes the transformd parsetree ast classes and produces javascript.    
    * *jslib.py* and *jsmap.py* - provides helper functions that gets compiled with the python.
    * *parsetree.py* - contains the datastructure for the intermediate ast.
    

    
