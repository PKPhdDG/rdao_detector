#!/usr/bin/env python3.8

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

import argparse
import config as c
from helpers import lock_types_str, deadlock_causes_str
from helpers.rdao_helper import get_operation_from_edge, get_operation_name_from_edge, get_resource_name_from_edge
from itertools import chain
import logging
from mascm_generator import create_ast, create_mascm
from os.path import join, dirname
from rdao import detect_atomicity_violation, detect_deadlock, detect_order_violation, detect_race_condition


def functions_pair(arg) -> tuple:
    """ Function split arguments using coma as delimiter """
    safe_replaces = {
        "inc_op": "++",
        "dec_op": "--",
        "increment_operator": "++",
        "decrement_operator": "--"
    }
    if not arg:
        return tuple()
    result = list()
    for pair in arg.split(","):
        if pair in safe_replaces:
            result.append(safe_replaces[pair])
        else:
            result.append(pair)
    return tuple(result)


parser = argparse.ArgumentParser(description='Detect RDAO Bugs')
parser.add_argument('path', type=str, help="Paths to source code")
parser.add_argument(
    '--log-level', choices=(logging.DEBUG, logging.INFO, logging.WARN, logging.ERROR, logging.CRITICAL),
    default=logging.INFO
)
parser.add_argument(
    '--forward-rel-pairs', type=functions_pair, help="Pairs of functions with forwards relation", default="", nargs="+"
)
parser.add_argument(
    '--backward-rel-pairs', type=functions_pair, help="Pairs of functions with backward relation", default="", nargs="+"
)
parser.add_argument(
    '--symmetric-rel-pairs', type=functions_pair, help="Pairs of functions with symmetric relation", default="",
    nargs="+"
)
parser.add_argument('--version', action='version', version=f"%(prog)s {__version__}")


def main():
    """ Main function
    """
    args = parser.parse_args()
    c.relations['forward'].extend(args.forward_rel_pairs)
    c.relations['backward'].extend(args.backward_rel_pairs)
    c.relations['symmetric'].extend(args.symmetric_rel_pairs)
    logging.basicConfig(filename=join(dirname(__file__), "rdao.log"), level=args.log_level)
    mascm = create_mascm(create_ast(args.path))

    print("Race conditions:")
    for edge in detect_race_condition(mascm):
        print(f"\tRace condition detected in element: {edge}")
        print("\tError can be found in")
        print(f"\t\t{edge.first.node.coord}")
        print("\tDetected race condition is linked with")
        print(f"\t\tresource: {get_resource_name_from_edge(edge)}")
        print(f"\t\tdeclared in {edge.second.node.coord}\n")
    print("="*60)

    print("Deadlocks:")
    for cause, edges in detect_deadlock(mascm):
        print(f"\tDeadlock detected involving a set of locks: {set((edge.first for edge in chain(*edges)))}")
        print("\t\tDeadlock cause:", deadlock_causes_str[cause])
        print("\tLocking operations can be found in:")
        for edge in chain(*edges):
            print(f"\t\t{edge.second.node.coord}", end=" ")
            print(f"using mutex variable {edge.first.name} of type {lock_types_str[edge.first.type]}")
    print("="*60)

    print("Atomicity violations:")
    for collection in detect_atomicity_violation(mascm):
        for f_edge, s_edge, *rest in collection:
            f_name = get_operation_name_from_edge(f_edge)
            s_name = get_operation_name_from_edge(s_edge)
            print(f"\tAtomicity violation detect for pair: {f_name}, {s_name}")
            print(f"\t\t{f_name} is located in: {get_operation_from_edge(f_edge).node.coord}")
            print(f"\t\t{s_name} is located in: {get_operation_from_edge(s_edge).node.coord}")
            for edge in rest:
                print(f"\t\tViolation is cause by: {get_operation_name_from_edge(edge)}")
                print(f"\t\tViolating operation is located in: {get_operation_from_edge(edge).node.coord}")
    print("="*60)

    print("Order violations:")
    for op1, op2, resource in detect_order_violation(mascm):
        print(f"\tOrder violation detected for pair: {op1.name}, {op2.name}")
        print(f"\t\t{op1.name} is located in {op1.node.coord}")
        print(f"\t\t{op2.name} is located in {op2.node.coord}")
        print("\tDetected order violation is linked with ")
        print(f"\t\tresource: {resource.get_resource_names_set()}")
        print(f"\t\tdeclared in {resource.node.coord}\n")


if "__main__" == __name__:
    main()
