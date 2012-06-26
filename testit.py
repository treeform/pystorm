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
# py2js_test.py
#
# Unit Tests for py2js
# 
# Usage: 
# python py2js_test.py
#
# Test that javascript can be generated from each of the python scripts in one or more directories
# Run both python and the generated javascript to check that the output is the same
#

import os
import os.path
import unittest
import sys

from pyfrontend import pyread
from jsbackend import jswrite

# configuration section
       
# relative path to directories where tests are stored
testdirs = ['tests/basic', 'tests/functions', 'tests/strings', 'tests/lists', 'tests/modules', 'tests/libraries']
# testdirs = ["tests/errors"]

# command to run python script
python_command = 'python'

# command to run javascript program (tested with spidermonkey)
#js_command = 'js'
js_command = 'node'

# js test harness to create
js_harness = os.path.join("tests","unittestdata.js")

# configuration section end

class Py2jsTester(unittest.TestCase):

    def configure(self,path):
        self.path = path
        self.pypath = path + ".py"
        self.jspath = path + ".js"

    
    def setUp(self):
        pass

class GenerateTester(Py2jsTester):

    def configure(self,path):
        Py2jsTester.configure(self,path)

    def shortDescription(self):
        return "generating: "+self.path

    def setUp(self):
        try:
            os.unlink(self.jspath)
        except:
            pass
        self.completed = False

    def runTest(self):
        self.error = ''
        try:
            code = pyread(self.pypath)
            jscode = jswrite(code,self.pypath)
            jsfile = open(self.jspath,"w")
            jsfile.write(jscode)
            self.completed = True
        except Exception, ex:
            self.error = str(ex)
        
class ExecuteTester(Py2jsTester):

    def configure(self,gtest,path,python_cmd,js_cmd):
        self.gtest = gtest
        self.pyoutpath = path + '_py.out'
        self.jsoutpath = path + '_js.out'
        self.python_cmd = python_cmd
        self.js_cmd = js_cmd
        Py2jsTester.configure(self,path)
    
    def shortDescription(self):
        return "Executing: "+self.path

    def setUp(self):
        try:
            os.unlink(self.pyoutpath)
        except:
            pass
        try:
            os.unlink(self.jsoutpath)
        except:
            pass
        pass

    def runTest(self):
        self.assertEqual(self.gtest.completed,True,"Generation Error: "+self.gtest.error)        
        cmdline = self.python_cmd + ' ' + self.pypath + ' > ' + self.pyoutpath
        os.system(cmdline)
        cmdline = self.js_cmd + ' ' + self.jspath + ' > ' + self.jsoutpath
        os.system(cmdline)
        jsout = open(self.jsoutpath,"r")
        pyout = open(self.pyoutpath,"r")
        jscontents = jsout.read().strip()
        pycontents = pyout.read().strip()
        # print "\n"
        # print "js("+jscontents+")"
        # print "py("+pycontents+")"
        self.assertEqual(jscontents,pycontents,"different output")
        jsout.close()
        pyout.close()

generate_tests = []
execute_tests = []

harness = open(js_harness,"w")
harness.write("document.write('<pre>\\n');");
harness.write("tests_start();\n");
# loop through each of the test dirs 
for testdir in testdirs:
    for f in os.listdir(testdir):
        if f.endswith(".py"):
            if len(sys.argv) > 1 and sys.argv[1] not in testdir + "/" + f:
                continue
            f = f[:-3]        
            g = GenerateTester()
            g.configure(os.path.join(testdir,f))
            subdir = os.path.split(testdir)[1]
            harness.write("test('"+subdir + "/" + f + "');\n");    
            generate_tests.append(g)
            t = ExecuteTester()
            t.configure(g,os.path.join(testdir,f),python_command,js_command)
            execute_tests.append(t)
harness.write("tests_end();\n");
harness.write("document.write('</pre>\\n');");
harness.close()

suite = unittest.TestSuite()

print "Generating..."
generator_errors = 0
for t in generate_tests:
    t.setUp()
    t.runTest()
    if not t.completed:
        generator_errors += 1
print "...complete (%d) errors."%generator_errors
print 

for t in execute_tests:
    suite.addTest(t)

# now try and execute the python and javascript files, and compare the output
unittest.TextTestRunner(verbosity=2).run(suite)

