# Rational

Maybe I am just tired of coffee script compiler. Maybe python is a better platform then node. Maybe I am just spoild being able to run same code on the client as on the server. I just want coffee script to be python. I make it happen.

Python to javascript landsape is graveyard unfinished compilers. Why not take a compiler thats simple and have a good number of tests and try to breathe some life into it. This is what I have done with Niall McCarroll compiler.

Pystorm will never be a 100% python compatible. But i hope it will be a decent subset of langauge features for python programmers to feel at home.
One probalby will never be able to take a full python program and translate it into js.  But one could easly write a js program using pystorm and that is its goal. To bring a nicer way to writing client side apps.
# Running

python pystorm.py file.py > file.js

All import statements in the file pack it right into the source.  For a browser app one would probalby have a single file they call that importas everything else the app needs.

# Hacking

What each file does:

* __pystrom.py__ - main 
* __pyfrontend.py__ - this file reads the python's ast and transforms it a little bit into parsetree's classes.
* __jsbackend.py__ - this is the backend part, takes the transformd parsetree ast classes and produces javascript.    
* __jslib.py__ and __jsmap.py__ - provides helper functions that gets compiled with the python.
* __parsetree.py__ - contains the datastructure for the intermediate ast.
    

    
