#!/usr/bin/env python3.8

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

compiler_cmd = "gcc"
main_function_name: str = "main"  # Name of main function in application

function_using_resources = {'printf'}

# Builtin elemental functions
ignored_c_functions: tuple = ("fscanf", "printf", "strlen", "memcpy", "memset", "free", "fopen", "fclose", 'strerror',
                              'time', 'rand', 'va_start', 'va_end', 'va_arg')
relations: dict = {  # Names of functions between which there are sequential relationships
    'forward': [],
    'backward': [],
    'symmetric': []
}

PTHREAD_MUTEX_DEFAULT_VAL = "PTHREAD_MUTEX_NORMAL"

