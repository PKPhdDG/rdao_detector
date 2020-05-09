#!/usr/bin/env python3.8

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

from collections import defaultdict
import config as c
from helpers import expressions as e
import logging
from mascm import Operation, TimeUnit
import re
from types import coroutine


def get_time_unit_edges(time_unit: TimeUnit, edges: list) -> coroutine:
    """ Coroutine which allow get edges for given time unit from set of all edges
    :param time_unit: Given time unit
    :param edges: List of all edges
    :return:
    """
    thread_creation = list()
    ignored_edges = list()  # Set of edges which have to be ignored, because they are on the first and last time unit
    for edge in edges:
        f, s = edge
        if (isinstance(f, Operation) and f.thread_index > 0) or (isinstance(s, Operation) and s.thread_index > 0):
            break
        if isinstance(f, Operation) and (f.name == "pthread_create"):
            thread_creation.append(True)
        elif isinstance(f, Operation) and (f.name == "pthread_join"):
            thread_creation.pop()
        if not thread_creation:
            ignored_edges.append(edge)

    for thread in time_unit:
        for edge in (e for e in edges if e not in ignored_edges):
            if isinstance(edge.first, Operation) and edge.first.is_operation_of_thread(thread):
                yield edge
            elif isinstance(edge.second, Operation) and edge.second.is_operation_of_thread(thread):
                yield edge
            else:
                logging.debug(f"Skipping edge: {edge}")


def get_time_units_graphs(time_units: list, edges: list) -> defaultdict:
    """ Function return dict with graphs for given time units
    :param time_units: List of time units
    :param edges: List of all edges
    :return: Collection of edges which build graphs for given time units
    """
    graphs = defaultdict(list)
    is_mutex = False
    for unit in time_units:
        key = str(unit)
        for edge in get_time_unit_edges(unit, edges):
            if re.match(e.mutex_exp, str(edge.first)) or re.match(e.mutex_exp, str(edge.second)):
                graphs[key].append(edge)
                is_mutex = not is_mutex
            elif re.match(e.resource_exp, str(edge.first)) or re.match(e.resource_exp, str(edge.second)):
                graphs[key].append(edge)
            elif is_mutex:
                graphs[key].append(edge)
            else:
                logging.debug(f"Skipping edge: {edge}")
    return graphs
