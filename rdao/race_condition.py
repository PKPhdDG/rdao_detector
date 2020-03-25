#!/usr/bin/env python3.7

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.2"

import config as c
from helpers import get_time_units_graphs, expressions as e
from itertools import combinations
from mascm import MultithreadedApplicationSourceCodeModel as MASCM
import re
from typing import Optional
from types import coroutine


class GraphComparator:
    """ Object of this class allow to compare two subgraphs """
    def __init__(self, first: Optional[list] = None, second: Optional[list] = None):
        self.first, self.second = first, second

    def locate_race_condition(self) -> list:
        """ Method detect operations casing race condition
        :return:
        """
        if (self.first is None) or (self.second is None):
            raise ValueError("Comparator does not contain enough graphs")

        possible_conflicts = list()
        resource_edges = ([], [])
        locks = ([], [])
        resources = ([], [])
        graphs = ([], [])
        for index, edges in enumerate((self.first, self.second)):
            possible_race_condition = True
            for edge in edges:
                if re.match(e.mutex_lock_edge_exp, str(edge)):
                    possible_race_condition = False
                    graphs[index].append(edge)
                    locks[index].append(edge.first)
                elif re.match(e.mutex_unlock_edge_exp, str(edge)):
                    possible_race_condition = True
                    graphs[index].append(edge)
                    locks[index].append(edge.second)
                elif re.match(e.usage_edge_exp, str(edge)):
                    graphs[index].append(edge)
                    resources[index].append(edge.second)
                    resource_edges[index].append(edge)
                    if possible_race_condition:
                        possible_conflicts.append(edge)
                elif re.match(e.dependency_edge_exp, str(edge)):
                    graphs[index].append(edge)
                    resources[index].append(edge.first)
                    resource_edges[index].append(edge)
                    if possible_race_condition:
                        possible_conflicts.append(edge)
                elif c.DEBUG:
                    print(f"Skipped edge: {edge}")

        if (not possible_conflicts) and (locks[0] != locks[1]):
            intersection = set(resources[0]).intersection(resources[1])
            if intersection:
                return resource_edges[0] + resource_edges[1]
            else:
                return []

        intersection = set(resources[0]).intersection(resources[1])
        if not intersection:
            return []

        return possible_conflicts

    def can_be_compared(self) -> bool:
        """ Method allow check there is possible to compare """
        return (self.first is not None) and (self.second is not None)


def detect_race_condition(mascm: MASCM) -> coroutine:
    """ Function is responsible for detecting race condition using MASCM """
    time_units = [unit for unit in mascm.time_units if len(unit) > 1]  # Do not check units with one thread only
    if not time_units:
        return None

    graphs = get_time_units_graphs(time_units, mascm.edges)  # Build full graphs for every time unit

    reported_op = list()
    subgraphs = list()
    for unit in time_units:
        edges = graphs[str(unit)]
        for thread_num in (mascm.threads.index(thread) for thread in unit):
            thread_edges = [edge for edge in edges if f"o{thread_num}" in str(edge)]
            if not thread_edges:
                raise ValueError(f"Unexpected situation for thread no. {thread_num} in time unit {unit}")
            # if (len(thread_edges) == 1) and re.match(e.usage_edge_exp, str(thread_edges[0])):
            #     yield thread_edges[0]
            subgraph = list()
            for edge in thread_edges:
                if re.match(e.mutex_lock_edge_exp, str(edge)):
                    subgraph.append(edge)
                elif re.match(e.mutex_unlock_edge_exp, str(edge)):
                    subgraph.append(edge)
                elif re.match(e.dependency_edge_exp, str(edge)):
                    subgraph.append(edge)
                if re.match(e.usage_edge_exp, str(edge)):
                    subgraph.append(edge)
            subgraphs.append(subgraph)

    for s1, s2 in combinations(subgraphs, 2):
        comparator = GraphComparator(s1, s2)
        if not comparator.can_be_compared():
            if c.DEBUG:
                print(f"Skipping compare of pair: {s1}, {s2}")
            continue
        for op in comparator.locate_race_condition():
            if op not in reported_op:
                reported_op.append(op)
                yield op
