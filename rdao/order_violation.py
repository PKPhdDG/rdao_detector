#!/usr/bin/env python3.8

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"


from mascm import Operation, Resource
from mascm import MultithreadedApplicationSourceCodeModel as MASCM
from types import coroutine


def detect_order_violation(mascm: MASCM) -> coroutine:
    """ Function is responsible for detecting order violation using MASCM """
    edges = mascm.relations.forward + mascm.relations.backward + mascm.relations.symmetric
    for op1, op2 in edges:
        op1_pattern = f"o{op1.thread.index},{op1.index}"

        for edge in mascm.edges:
            if op1_pattern not in str(edge):
                continue

            second_resource = isinstance(edge.second, Resource)
            first_resource = isinstance(edge.first, Resource)
            if not second_resource and not first_resource:
                continue
            resource = edge.second if second_resource else edge.first
            op2_pattern = f"o{op2.thread.index},{op2.index}"
            usage_edge_pattern = f"({op2_pattern}, {resource})"
            dependency_edge_pattern = f"({resource}, {op2_pattern})"
            if any((edge for edge in mascm.edges if str(edge) in (usage_edge_pattern, dependency_edge_pattern))):
                yield (op1, op2, resource)


