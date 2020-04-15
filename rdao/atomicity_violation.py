#!/usr/bin/env python3.7

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.3"

from helpers import get_time_units_graphs, expressions as e
from itertools import combinations
from mascm import MultithreadedApplicationSourceCodeModel as MASCM, Resource
import re
import sys
from types import coroutine


def detect_violation(first: list, second: list, relation: list) -> list:
    """ Function is responsible for detect """
    f_op, s_op = relation
    # TODO Re-implement code bellow to detect critical sectionsu
    op_edges = list((edge for edge in first if edge.first in relation or edge.second in relation))

    used_resources = list()
    for edge in op_edges:
        if isinstance(edge.first, Resource):
            used_resources.append(edge.first)
        elif isinstance(edge.second, Resource):
            used_resources.append(edge.second)




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
        result = set()
        result.add(detect_violation(first, second, relation))
        result.add(detect_violation(second, first, relation))
        yield result


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
