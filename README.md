# C to Multithreaded Application Source Code Model

This simple application convert C source code to Multithreaded Application Source Code Model via AST.

Source code used to creating MAM have to be purified.
~~To purify C code use `purize_c.sh` script, when parameters are names of C files.~~
~~Script this work with `gcc` compiler so you have to add `gcc` into `$PATH` variable.~~
Application do it automatically but there is need to install GCC and add path to gcc into PATH variable. 

## GCC
Install CodeBlocks with gcc using codeblocks-17.12mingw-setup.exe which is available [here](http://www.codeblocks.org/downloads/26)
Add path to gcc to system variable PATH

## Interesting links
- https://github.com/eliben/pycparser
- https://eli.thegreenplace.net/2015/on-parsing-c-type-declarations-and-fake-headers
