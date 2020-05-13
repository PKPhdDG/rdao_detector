#!/usr/bin/env python3.8

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

from collections import defaultdict
from helpers import get_time_units_graphs, expressions as e
from itertools import combinations
import logging
from mascm import MultithreadedApplicationSourceCodeModel as MASCM, Operation
import re
from types import coroutine


class GraphComparator:
    """ Object of this class allow to compare two subgraphs """
    def __init__(self, first: list, second: list, ignored_edges: list = []):
        self.first, self.second = first, second
        self.ignored_edges = ignored_edges

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
                if edge in self.ignored_edges:
                    continue
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
                else:
                    logging.debug(f"Skipping edge: {edge}")

        if (not possible_conflicts) and not set(locks[0]).intersection(locks[1]):
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


def prepare_ignored_edges(thread_index: int, edges: list) -> list:
    """ Function check set of edges to detect which edges should be ignored

    :param thread_index: Index of thread
    :param edges: list of all edges
    :return: List of ignored edges
    """
    thread_creation = list()
    # Set of edges which have to be ignored, because they are before pthread_create and after pthread_join
    ignored_edges = list()
    for edge in edges:
        f, s = edge
        if (isinstance(f, Operation) and f.thread.index > thread_index) or \
                (isinstance(s, Operation) and s.thread.index > thread_index):
            break
        elif (isinstance(f, Operation) and f.thread.index < thread_index) or \
                (isinstance(s, Operation) and s.thread.index < thread_index):
            continue
        if isinstance(f, Operation) and (f.name == "pthread_create"):
            thread_creation.append(True)
        elif isinstance(f, Operation) and (f.name == "pthread_join"):
            thread_creation.pop()
        if not thread_creation:
            ignored_edges.append(edge)
    return ignored_edges


def detect_race_condition(mascm: MASCM) -> coroutine:
    """ Function is responsible for detecting race conditions using MASCM """
    # Do not check units with one thread only
    # Also remove redundant time units
    cond = lambda unit, tu, i: (unit not in tu[:i]) and (len(unit) > 1)
    time_units = [unit for i, unit in enumerate(mascm.time_units) if cond(unit, mascm.time_units, i)]
    if not time_units:
        return None

    graphs = get_time_units_graphs(time_units, mascm.edges)  # Build full graphs for every time unit
    subgraphs = defaultdict(list)
    for unit in time_units:
        edges = graphs[str(unit)]
        for thread_num in (mascm.threads.index(thread) for thread in unit):
            thread_edges = [edge for edge in edges if f"o{thread_num}" in str(edge)]
            if not thread_edges:
                logging.debug(f"Unexpected situation for thread no. {thread_num} in time unit {unit}")
                continue

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
            subgraphs[str(unit)].append(subgraph)

    reported_op = list()
    for _, tu_subraphs in subgraphs.items():
        for s1, s2 in combinations(tu_subraphs, 2):
            # Dirty hack to get threads of indexes
            s1_thread = s1[0][1].thread if isinstance(s1[0][1], Operation) else s1[0][0].thread
            s2_thread = s2[0][1].thread if isinstance(s2[0][1], Operation) else s2[0][0].thread
            if s1_thread == s2_thread:
                continue
            ignored_edges = []
            if s1_thread.depth < s2_thread.depth:
                ignored_edges = prepare_ignored_edges(s1_thread.index, mascm.edges)
            elif s1_thread.depth == s2_thread.depth:
                logging.debug(f"Comparing threads t1({s1_thread}) and t2({s2_thread}) with equal depth!")
            else:
                ignored_edges = prepare_ignored_edges(s2_thread.index, mascm.edges)

            comparator = GraphComparator(s1, s2, ignored_edges)
            if not comparator.can_be_compared():
                logging.debug(f"Skipping compare of pair: {s1}, {s2}")
                continue
            for op in comparator.locate_race_condition():
                if op not in reported_op:
                    reported_op.append(op)
                    yield op
