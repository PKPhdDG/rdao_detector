#!/usr/bin/env python3.7

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.2"

DEBUG = True

main_function_name: str = "main"  # Name of main function in application
# Builtin elemental functions
ignored_c_functions: tuple = ("fscanf", "printf", "strlen", "memcpy", "memset", "free", "fopen", "fclose", 'strerror',
                              'time', 'rand', 'va_start', 'va_end', 'va_arg')
relations: dict = {  # Names of functions between which there are sequential relationships
    'forward': [],
    'backward': [],
    'symmetric': []
}
