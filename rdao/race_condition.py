#!/usr/bin/env python3.7

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.2"

import config as c
from helpers import get_time_units_graphs, expressions as e
from mascm import MultithreadedApplicationSourceCodeModel as MASCM
import re
from typing import Optional
from types import coroutine


class GraphComparator:
    """ Object of this class allow to compare two subgraphs """
    def __init__(self, first: Optional[list] = None, second: Optional[list] = None):
        self.first, self.second = first, second

    def compare(self) -> bool:
        if (self.first is None) or (self.second is None):
            raise ValueError("Comparator does not contain enough graphs")
        order = [[], []]

        for index, edges in enumerate((self.first, self.second)):
            for edge in edges:
                if re.match(e.mutex_lock_edge_exp, str(edge)):
                    order[index].append(edge.first)
                elif re.match(e.mutex_unlock_edge_exp, str(edge)):
                    order[index].append(edge.second)
                elif re.match(e.usage_edge_exp, str(edge)):
                    order[index].append(edge.second)
                elif re.match(e.dependency_edge_exp, str(edge)):
                    order[index].append(edge.first)
                elif c.DEBUG:
                    print(f"Skipped edge: {edge}")

        comp = lambda a, b: all(i in b for i in a)
        if comp(order[0], order[1]) or comp(order[1], order[0]):
            return True  # There is no race condition between two threads
        return False  # There is race condition between two threads


    def second_is_first(self) -> None:
        """ Method make second graph first, and second graph is None """
        self.first = self.second
        self.second = None

    def can_be_compared(self) -> bool:
        """ Method allow check there is possible to compare """
        return (self.first is not None) and (self.second is not None)

    def feed(self, graph):
        """ Method allow feed comparator """
        self.second_is_first()
        self.second = graph


def detect_race_condition(mascm: MASCM) -> coroutine:
    """ Function is responsible for detecting race condition using MASCM """
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
            if (len(thread_edges) == 1) and re.match(e.usage_edge_exp, str(thread_edges[0])):
                yield thread_edges[0]
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

    comparator = GraphComparator()
    for subgraph in subgraphs:
        comparator.feed(subgraph)
        if comparator.can_be_compared():
            if not comparator.compare():
                for s_graph in (comparator.first, comparator.second):
                    for edge in s_graph:
                        if re.match(e.usage_edge_exp, str(edge)) or re.match(e.dependency_edge_exp, str(edge)):
                            yield edge

    pass
