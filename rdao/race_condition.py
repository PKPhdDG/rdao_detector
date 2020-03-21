#!/usr/bin/env python3.7

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.2"

from helpers import get_time_units_graphs, expressions as e
from mascm import MultithreadedApplicationSourceCodeModel as MASCM
import re
from types import coroutine


def detect_race_condition(mascm: MASCM) -> coroutine:
    """ Function is responsible for detecting race condition using MASCM """
    time_units = [unit for unit in mascm.time_units if len(unit) > 1]  # Do not check units with one thread only
    if not time_units:
        return None

    graphs = get_time_units_graphs(time_units, mascm.edges)  # Build full graphs for every time unit

    for unit in time_units:
        edges = graphs[str(unit)]
        for thread_num in (mascm.threads.index(thread) for thread in unit):
            thread_edges = [edge for edge in edges if f"o{thread_num}" in str(edge)]
            if not thread_edges:
                raise ValueError(f"Unexpected situation for thread no. {thread_num} in time unit {unit}")
            if (len(thread_edges) == 1) and  re.match(e.edge_exp, str(thread_edges[0])):
                yield thread_edges[0]
            order = list()
            for edge in thread_edges:
                if re.match(e.mutex_exp, str(edge.first)) or re.match(e.mutex_exp, str(edge.second)):
                    order.append(edge)

