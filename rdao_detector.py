#!/usr/bin/env python3.7

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.2"

import argparse
from helpers import lock_types_str, deadlock_causes_str
from itertools import chain
from mascm_generator import create_ast, create_mascm
from rdao import detect_deadlock, detect_race_condition

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

    print("Deadlocks:")
    for cause, el in detect_deadlock(mascm):
        print(f"\tDeadlock detected involving a set of locks: {set((edge.first for edge in chain(*el)))}")
        print("\t\tDeadlock cause:", deadlock_causes_str[cause])
        print("\tLocking operations can be found in:")
        for edge in chain(*el):
            print(f"\t\t{edge.second.node.coord}", end=" ")
            print(f"using mutex variable {edge.first.name} of type {lock_types_str[edge.first.type]}")
    print("="*60)


if "__main__" == __name__:
    main()
