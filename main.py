#!/usr/bin/env python3

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"

from multithreaded_application_model import MultithreadedApplicationModel
from pycparser import parse_file

if "__main__" == __name__:
    ast = parse_file("tests/example_c_sources/atomicity_violation0.c.pure", use_cpp=False)
    mam = MultithreadedApplicationModel.create_multithreaded_application_model(ast)
    print(mam)
