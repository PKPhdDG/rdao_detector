#!/usr/bin/env python3

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.2"

import argparse
from mascm_generator import create_ast, create_mascm

parser = argparse.ArgumentParser(description='Detect RDAO Bugs')
parser.add_argument('path', type=str, help="Paths to source code")


def main():
    """ Main function
    """
    args = parser.parse_args()
    mascm = create_mascm(create_ast(args.path))
    raise NotImplementedError("This program is not implemented yet.")


if "__main__" == __name__:
    main()
