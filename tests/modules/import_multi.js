// generated by py2js from tests/modules/import_multi.py


var __name__ = '__main__';

// generated by py2js from tests/modules/imported/modulec.py


__name__ = 'imported.modulec';


// __main__->imported.modulec
// generated by py2js from tests/modules/imported/submodules/submodulea.py


__name__ = 'imported.submodules.submodulea';


// imported.modulec->imported.submodules.submodulea
var imported = {};
imported.submodules = {};
imported.submodules.submodulea = {};
imported.submodules.submodulea.foo = function()  {
    console.log(String('imported.modules.submodules.modulea.foo()'));
}



__name__ = 'imported.modulec';


imported.modulec = {};
imported.modulec.foo = function()  {
    console.log(String('imported.modulec.foo()'));
    imported.submodules.submodulea.foo();
}



__name__ = '__main__';


function foo()  {
    console.log(String('foo'));
    imported.modulec.foo();
}
foo();
