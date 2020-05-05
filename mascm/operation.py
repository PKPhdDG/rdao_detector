__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

import config as c
import logging
from helpers.exceptions import MASCMException
from mascm.edge import Edge
from mascm.lock import Lock
from mascm.resource import Resource
from pycparser.c_ast import *
from typing import Optional


class Operation:
    """Operation class"""
    __dependency_operation_types = (If,)

    def __init__(self, node: Node, thread, thread_index: int, function: str):
        """Ctor
        :param node: Node obj
        :param thread: Thread object
        :param thread_index: Thread index in the mascm
        :param function name in which operation is called
        """
        self.__node = node
        self.__thread = thread
        self.__thread_index = thread_index
        self.__thread.add_operation(self)
        self.__operation_number = self.__thread.num_of_operations()
        self.__name = ""
        self.__args = list()
        self.__ignored_arg_types = (Constant,)
        self.__is_return = False
        self.__function = function
        self.__is_loop_body_operation = False  # Used generally for pthread_mutex_lock/unlock
        self.__is_if_else_block_operation = False
        self.__related_mutex = None
        if isinstance(self.__node, FuncCall):
            self.__name = self.__node.name.name
            if self.__node.args is not None:
                self.__add_resources(self.__node.args.exprs)
        elif isinstance(self.__node, UnaryOp):
            self.__name = self.__node.op
            self.__add_resources([self.__node.expr])
        elif isinstance(self.__node, Return):
            self.__name = "return"
            self.__is_return = True
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

    @property
    def function(self) -> str:
        """ Function name str """
        return self.__function

    @property
    def is_return(self) -> bool:
        """ If this is return operation this method return true
        """
        return self.__is_return

    @property
    def use_resources(self) -> bool:
        """ Operation use some resources """
        return bool(self.__args)

    @property
    def is_if_else_block_operation(self) -> bool:
        """ Getter
        :return: Boolean value
        """
        return self.__is_if_else_block_operation

    @is_if_else_block_operation.setter
    def is_if_else_block_operation(self, value: bool):
        """Setter
        :param value: Boolean value
        """
        logging.debug(f"Setting new value for is_if_else_bock_operation: {value}")
        self.__is_if_else_block_operation = value

    @property
    def is_loop_body_operation(self) -> bool:
        """ Getter
        :return: Boolean value
        """
        return self.__is_loop_body_operation

    @is_loop_body_operation.setter
    def is_loop_body_operation(self, value: bool):
        """ Setter
        :param value: Boolean value
        """
        self.__is_loop_body_operation = value

    @property
    def related_mutex(self) -> Lock:
        """ Getter
        :return: Boolean value
        """
        return self.__related_mutex

    @related_mutex.setter
    def related_mutex(self, value: Lock):
        """ Setter
        :param value: Boolean value
        """
        if self.__related_mutex is not None:
            raise MASCMException("Trying link mutex and operation which locks other mutex")
        logging.debug(f"Setting new value for related_mutex: {value}")
        self.__related_mutex = value

    def add_use_resource(self, resource: Resource) -> None:
        """ Method add resource to resource list """
        self.__args.append(resource)

    def use_the_resource(self, resource: Resource) -> bool:
        """ Method check given resource is used by operation
        :param resource: Resource object
        :return: Boolean value
        """
        for arg in self.__args:
            if resource.has_names(arg.names):
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

    def create_edge_with_resource(self, resource: Resource) -> Optional[Edge]:
        """ Method create correct edge for relation operation - edge """
        if isinstance(self.__node, FuncCall) and (self.name in c.function_using_resources):
            return self.create_dependency_edge(resource)
        elif isinstance(self.__node, self.__dependency_operation_types):
            return self.create_dependency_edge(resource)
        elif isinstance(self.__node, FuncCall) and (self.name in ('memcpy', 'memset')) \
                and resource.has_names(self.__args[1].names):
            return self.create_dependency_edge(resource)
        elif isinstance(self.__node, ID):
            return self.create_dependency_edge(resource)
        elif isinstance(self.__node, BinaryOp):
            return self.create_dependency_edge(resource)
        elif self.name == '&':
            return None
        return self.create_usage_edge(resource)

    def __eq__(self, other):
        return self.__thread_index == other.__thread_index and self.__operation_number == other.__operation_number

    def __repr__(self):
        return "o{},{}".format(self.__thread_index, self.__operation_number)
