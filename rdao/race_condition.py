#!/usr/bin/env python3.8

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

from helpers import get_time_units_graphs, expressions as e
from itertools import combinations
import logging
from mascm import MultithreadedApplicationSourceCodeModel as MASCM, Operation
import re
from typing import Optional
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
        if (isinstance(f, Operation) and f.thread_index > thread_index) or \
                (isinstance(s, Operation) and s.thread_index > thread_index):
            break
        elif (isinstance(f, Operation) and f.thread_index < thread_index) or \
                (isinstance(s, Operation) and s.thread_index < thread_index):
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
    time_units = [unit for unit in mascm.time_units if len(unit) > 1]  # Do not check units with one thread only
    if not time_units:
        return None

    graphs = get_time_units_graphs(time_units, mascm.edges)  # Build full graphs for every time unit
    threads_to_find_ignored_edges = []  # Default t0 should be here
    subgraphs = list()
    for unit in time_units:
        edges = graphs[str(unit)]
        for thread_num, thread in zip((mascm.threads.index(thread) for thread in unit), unit):
            thread_edges = [edge for edge in edges if f"o{thread_num}" in str(edge)]
            if not thread_edges:
                logging.debug(f"Unexpected situation for thread no. {thread_num} in time unit {unit}")
                continue
            if thread not in threads_to_find_ignored_edges:
                threads_to_find_ignored_edges.append(thread)

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
            subgraphs.append(subgraph)

    reported_op = list()
    for subgraphs_pair, threads_pair in zip(combinations(subgraphs, 2), combinations(threads_to_find_ignored_edges, 2)):
        s1, s2 = subgraphs_pair
        t1, t2 = threads_pair
        ignored_edges = []
        if t1.depth < t2.depth:
            ignored_edges = prepare_ignored_edges(t1.index, mascm.edges)
        elif t1.depth == t2.depth:
            logging.debug(f"Comparing threads t1({t1}) and t2({t2}) with equal depth!")
        else:
            logging.critical(f"Unexpected situation t1({t1}) has greater depth than t2({t2})!")
        comparator = GraphComparator(s1, s2, ignored_edges)
        if not comparator.can_be_compared():
            logging.debug(f"Skipping compare of pair: {s1}, {s2}")
            continue
        for op in comparator.locate_race_condition():
            if op not in reported_op:
                reported_op.append(op)
                yield op
