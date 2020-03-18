#!/usr/bin/env python3

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.2"

import argparse
from collections import deque
from helpers.path import collect_c_project_files
from helpers.purifier import purify_file, purify_files
from mascm import create_mascm
from pycparser import parse_file

parser = argparse.ArgumentParser(description='Process AST to MASCM')
parser.add_argument('path', type=str, help="Paths to source code")


def create_ast(path: str) -> deque:
    """Function converting C code to AST
    :param path: Path to source code
    :return: deque object
    """
    try:
        ast = deque()
        ast.append(parse_file(purify_file(path)))
        return ast
    except IsADirectoryError:
        pass
    pure_files = purify_files(collect_c_project_files(path))
    ast = deque()
    for file in pure_files:
        ast.append(parse_file(file))
    return ast


def main() -> None:
    """ Main function
    """
    args = parser.parse_args()
    mascm = create_mascm(create_ast(args.path))
    print(mascm)


if "__main__" == __name__:
    main()
