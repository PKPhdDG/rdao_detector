# Race condition/Deadlock/Atomicity violation/Order violation Detector 
[![Static analysis](https://github.com/PKPhdDG/rdao_detector/actions/workflows/static-analysis.yml/badge.svg)](https://github.com/PKPhdDG/rdao_detector/actions/workflows/static-analysis.yml)

This simple application convert C source code to Multithreaded Application Source Code Model via AST, and using MASCM detecting RDAO bugs.

Source code used to creating MASCM have to be purified.
Application do it automatically but there is need to install GCC and add path to gcc into PATH variable. 

## GCC
Install GCC and add path to gcc to system variable PATH.
You can also install CodeBlocks with gcc which is available [here](http://www.codeblocks.org/downloads/26).


## Interesting links
- https://github.com/eliben/pycparser
- https://eli.thegreenplace.net/2015/on-parsing-c-type-declarations-and-fake-headers
