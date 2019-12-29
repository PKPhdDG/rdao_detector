#!/usr/bin/env python3

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"

import argparse
from collections import deque
from helpers.purifier import purify_file
from mascm import create_mascm, MultithreadedApplicationSourceCodeModel
import os
from pycparser import parse_file
from pycparser.c_parser import CParser

parser = argparse.ArgumentParser(description='Process AST to MASCM')
parser.add_argument('paths', type=str, nargs='+', help="Paths to source code")


def create_ast(path: str) -> CParser:
    """Function converting C code to AST
    :param path: Path to source code
    :return: CParser object
    """
    try:
        return parse_file(purify_file(path), use_cpp=False)
    except IsADirectoryError:
        raise NotImplementedError("Target is not a file")


def main():
    args = parser.parse_args()
    mascm = create_mascm(deque((create_ast(path) for path in args.paths)))
    print(mascm)


if "__main__" == __name__:
    main()
