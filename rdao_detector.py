#!/usr/bin/env python3.7

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.2"

import argparse
from mascm_generator import create_ast, create_mascm
from rdao.race_condition import detect_race_condition

parser = argparse.ArgumentParser(description='Detect RDAO Bugs')
parser.add_argument('path', type=str, help="Paths to source code")


def main():
    """ Main function
    """
    args = parser.parse_args()
    mascm = create_mascm(create_ast(args.path))
    print("Race conditions:")
    for el in detect_race_condition(mascm):
        print(f"\tRace condition detected in element: {el}")
        print("\tError can be found in")
        print(f"\t\t{el.first.node.coord}")
        print("\tDetected race condition is linked with ")
        print(f"\t\tresource {el.second.node.name} ")
        print(f"\t\tdeclared in {el.second.node.coord}\n")
    print("="*60)



if "__main__" == __name__:
    main()
