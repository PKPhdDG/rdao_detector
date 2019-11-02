#!/usr/bin/env python3

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"

import argparse
from collections import deque
from multithreaded_application_model import create_multithreaded_application_model, MultithreadedApplicationModel
import os
from pycparser import parse_file
from pycparser.c_parser import CParser

parser = argparse.ArgumentParser(description='Process AST to MAM')
parser.add_argument('paths', type=str, nargs='+', help="Paths to source code")


def create_ast(path: str) -> CParser:
    """Function converting C code to AST
    :param path: Path to source code
    :return: CParser object
    """
    if os.path.isfile(path):
        return parse_file(path, use_cpp=False)
    raise NotImplementedError("Target is not a file")


def create_mam(asts: list) -> MultithreadedApplicationModel:
    """ Function convert AST's into MAM
    :param asts: AST's list
    :return: MAM object
    """
    return create_multithreaded_application_model(asts)


def main():
    args = parser.parse_args()
    mam = create_mam(deque((create_ast(path) for path in args.paths)))
    print(mam)


if "__main__" == __name__:
    main()
