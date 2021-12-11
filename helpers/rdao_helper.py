#!/usr/bin/env python3.8

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "1.1"

from helpers.exceptions import RDAOException
from mascm.edge import Edge
from mascm.operation import Operation
from mascm.resource import Resource


def get_operation_from_edge(edge: Edge) -> Operation:
    """ Function get first found operation in edge """
    if isinstance(edge.first, Operation):
        return edge.first
    elif isinstance(edge.second, Operation):
        return edge.second
    else:
        RDAOException(f"Wrong constructed edge: {str(edge)}")


def get_resource_from_edge(edge: Edge) -> Resource:
    """ Function get resource from edge """
    if isinstance(edge.first, Resource):
        return edge.first
    elif isinstance(edge.second, Resource):
        return edge.second
    else:
        RDAOException(f"Given edge is not use or dependency edge: {str(edge)}")


def get_operation_name_from_edge(edge: Edge) -> str:
    """ Function get name of first found operation in edge """
    return get_operation_from_edge(edge).name


def get_resource_name_from_edge(edge: Edge) -> str:
    """ Function return name of the given operaiont """
    return get_resource_from_edge(edge).get_resource_names_set()
