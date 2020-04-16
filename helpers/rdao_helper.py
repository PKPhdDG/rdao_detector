#!/usr/bin/env python3.7

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.3"

from mascm.edge import Edge
from mascm.operation import Operation


def get_operation_from_edge(edge: Edge):
    """ Function get first found operation in edge """
    return edge.first if isinstance(edge.first, Operation) else edge.second


def get_operation_name_from_edge(edge: Edge) -> str:
    """ Function get name of first found operation in edge """
    return get_operation_from_edge(edge).name
