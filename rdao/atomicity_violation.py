#!/usr/bin/env python3.7

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.3"

from copy import copy
from collections import defaultdict
import config as c
from helpers import get_time_units_graphs, expressions as e
from itertools import combinations
from mascm import MultithreadedApplicationSourceCodeModel as MASCM, Resource
import re
import sys
from types import coroutine


class RDAOException(BaseException):
    """ RDAO Exception """
    pass


def group_operations_by_critical_section(graph: list) -> dict:
    """ Function is responsible for group operations by critical_sections  """
    critical_sections_operations = defaultdict(list)
    critical_sections_stack = []
    critical_section_number = 0
    for edge in graph:
        if re.match(e.mutex_lock_edge_exp, str(edge)):
            if not critical_sections_stack:
                critical_section_number += 1
            critical_sections_stack.append(edge.first)
            continue
        elif re.match(e.mutex_unlock_edge_exp, str(edge)):
            critical_sections_stack.remove(edge.second)
            continue
        if critical_sections_stack:
            if re.match(e.usage_edge_exp, str(edge)):
                critical_sections_operations[critical_section_number].append(
                    (edge.first, edge.second, copy(critical_sections_stack), edge)
                )
            elif re.match(e.dependency_edge_exp, str(edge)):
                critical_sections_operations[critical_section_number].append(
                    (edge.second, edge.first, copy(critical_sections_stack), edge)
                )
    return critical_sections_operations


def detect_violation(first: list, second: list, relation: list) -> list:
    """ Function is responsible for detect """
    EDGE_POS = 3
    f_op, s_op = relation
    def is_in_the_section(op, collection):
        return collection[0] == op
    critical_sections_operations = group_operations_by_critical_section(first)
    split_sections = list()
    operations_atomicity_violated = list()
    for _, section_ops in critical_sections_operations.items():
        for section_op in section_ops:
            if is_in_the_section(f_op, section_op) and not is_in_the_section(s_op, section_op):
                split_sections.append(section_op)
                operations_atomicity_violated.append(section_op[EDGE_POS])
            elif is_in_the_section(s_op, section_op) and not is_in_the_section(f_op, section_op):
                split_sections.append(section_op)
                operations_atomicity_violated.append(section_op[EDGE_POS])
    if len(split_sections) > 2:
        if c.DEBUG:
            print(f"Unexpected sections: {split_sections}", file=sys.stderr)
        raise RDAOException(f"Unexpected sections: {split_sections}")
    if len(split_sections) < 2:
        return []
    if c.DEBUG and split_sections[0][1] != split_sections[1][1]:
        print(f"Pair related operations use two different resources:{split_sections[0][1], split_sections[1][1]}",
              file=sys.stderr)

    shared_resource = split_sections[0][1]
    for edge in second:
        if re.match(e.usage_edge_exp, str(edge)) and (edge.second == shared_resource):
            operations_atomicity_violated.append(edge)
        elif re.match(e.dependency_edge_exp, str(edge)) and (edge.first == shared_resource):
            operations_atomicity_violated.append(edge)
    return operations_atomicity_violated


def forward_relation_violated(graph: list, relations: list) -> coroutine:
    """ Function detect atomicity violation in forward relation """
    print("atomicity violation for forward relation not implemented yet!", file=sys.stderr)
    yield None


def backward_relation_violated(graph: list, relations: list) -> coroutine:
    """ Function detect atomicity violation in backward relation """
    print("atomicity violation for backward relation not implemented yet!", file=sys.stderr)
    yield None


def symmetric_relation_violated(first: list, second: list, relations: list) -> coroutine:
    """ Function detect atomicity violation in symmetric relation """
    for relation in relations:
        results = list()
        result = detect_violation(first, second, relation)
        if result:
            results.append(result)
        result = detect_violation(second, first, relation)
        if result:
            results.append(result)
        yield results


def detect_atomicity_violation(mascm: MASCM) -> coroutine:
    """ Function is responsible for detecting atomicity violations using MASCM """
    time_units = [unit for unit in mascm.time_units if len(unit) > 1]  # Do not check units with one thread only
    if not time_units:
        return None

    graphs = get_time_units_graphs(time_units, mascm.edges)  # Build full graphs for every time unit

    subgraphs = list()
    for unit in time_units:
        edges = graphs[str(unit)]
        for thread_num in (mascm.threads.index(thread) for thread in unit):
            thread_edges = [edge for edge in edges if f"o{thread_num}" in str(edge)]
            if not thread_edges:
                raise ValueError(f"Unexpected situation for thread no. {thread_num} in time unit {unit}")

            subgraph = list()
            for edge in thread_edges:
                if re.match(e.mutex_lock_edge_exp, str(edge)):
                    subgraph.append(edge)
                elif re.match(e.mutex_unlock_edge_exp, str(edge)):
                    subgraph.append(edge)
                elif re.match(e.dependency_edge_exp, str(edge)):
                    subgraph.append(edge)
                elif re.match(e.usage_edge_exp, str(edge)):
                    subgraph.append(edge)
            if subgraph:
                subgraphs.append(subgraph)

    next(forward_relation_violated(subgraphs, mascm.relations.forward))
    next(backward_relation_violated(subgraphs, mascm.relations.backward))
    for f, s in combinations(subgraphs, 2):
        for violation in symmetric_relation_violated(f, s, mascm.relations.symmetric):
            yield violation
