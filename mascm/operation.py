__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

import config as c
from helpers.mascm_helper import extract_resource_name
import logging
from mascm.edge import Edge
from mascm.resource import Resource
from pycparser.c_ast import *


class Operation:
    """Operation class"""
    __dependency_operation_types = (If,)

    def __init__(self, node: Node, thread, thread_index: int, called_in_loop: bool):
        """Ctor
        :param node: Node obj
        :param thread: Thread object
        :param thread_index: Thread index in the mascm
        :param called_in_loop: Boolean value  which is True if operation is part of loop body
        """
        self.__node = node
        self.__thread = thread
        self.__thread_index = thread_index
        self.__thread.add_operation(self)
        self.__operation_number = self.__thread.num_of_operations()
        self.__name = ""
        self.__args = list()
        self.__ignored_arg_types = (Constant,)
        self.__is_last_action = False
        self.is_multiple_called = called_in_loop  # Used generally for pthread_mutex_lock/unlock
        if isinstance(self.__node, FuncCall):
            self.__name = self.__node.name.name
            if self.__node.args is not None:
                self.__add_resources(self.__node.args.exprs)
        elif isinstance(self.__node, UnaryOp):
            self.__name = self.__node.op
            self.__add_resources([self.__node.expr])
        elif isinstance(self.__node, Return):
            self.__name = "return"
            self.__is_last_action = True
        elif isinstance(self.__node, If):
            self.__name = "if"

    def __add_resources(self, resources: list) -> None:
        """ Method extract from objects resources
        :param resources: list of objects which can contains resources
        """
        for arg in resources:
            if isinstance(arg, BinaryOp):
                self.__args.append(Resource(arg.left))
                self.__args.append(Resource(arg.right))
            else:
                self.__args.append(Resource(arg))

    @property
    def thread_index(self) -> int:
        """ Thread index """
        return self.__thread_index

    @property
    def index(self):
        """ Operation index """
        return self.__operation_number

    @property
    def name(self) -> str:
        """ Name of operation if this is function call. In other case name is empty.
        :return: String value
        """
        return self.__name

    @property
    def args(self) -> list:
        """ Function arguments list is returned
        :return: List of arguments
        """
        return self.__args

    @property
    def node(self) -> Node:
        """ Node getter
        :return: Node
        """
        return self.__node

    def is_last_action(self) -> bool:
        """ If this is return operation this method return true
        :return: Boolean value
        """
        return self.__is_last_action

    def add_use_resource(self, resource: Resource) -> None:
        """ Method add resource to resource list """
        self.__args.append(resource)

    def has_func_use_the_resource(self, resource: Resource) -> bool:
        """ Method check given resource is used by operation
        :param resource: Resource object
        :return: Boolean value
        """
        for arg in self.__args:
            if resource.has_name(arg.name):
                return True
            else:
                if not isinstance(arg, self.__ignored_arg_types):
                    logging.warning(f"Operation {self} do not uses resource: {arg}")
        return False

    def is_operation_of_thread(self, other_thread) -> bool:
        """ Method check operation is operation of a given thread """
        return self.__thread == other_thread

    def create_usage_edge(self, resource: Resource) -> Edge:
        """ Method create usage edge """
        return Edge(self, resource)

    def create_dependency_edge(self, resource: Resource) -> Edge:
        """ Method create dependency edge """
        return Edge(resource, self)

    def create_edge_with_resource(self, resource: Resource) -> Edge:
        """ Method create correct edge for relation operation - edge """
        if isinstance(self.__node, FuncCall) and (self.name in c.function_using_resources):
            return self.create_dependency_edge(resource)
        elif isinstance(self.__node, self.__dependency_operation_types):
            return self.create_dependency_edge(resource)
        elif isinstance(self.__node, FuncCall) and (self.name in ('memcpy', 'memset')) \
                and resource.has_name(self.__args[1].name):
            return self.create_dependency_edge(resource)
        return self.create_usage_edge(resource)

    def __repr__(self):
        return "o{},{}".format(self.__thread_index, self.__operation_number)
