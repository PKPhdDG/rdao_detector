# C to Multithreaded Application Model

This simple application convert C source code to Multithreaded Application Model via AST.

Source code used to creating MAM have to be purize.
To purize C code use `purize_c.sh` script, when parameters are names of C files.
Script this work with `gcc` compiler so you have to add `gcc` into `$PATH` variable. 


## Interesting links
- https://github.com/eliben/pycparser
- https://eli.thegreenplace.net/2015/on-parsing-c-type-declarations-and-fake-headers