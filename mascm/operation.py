__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "1.1"

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

    def __init__(self, node: Node, thread, function: str):
        """Ctor
        :param node: Node obj
        :param thread: Thread object
        :param function name in which operation is called
        """
        self.__node = node
        self.__thread = thread
        self.__thread.add_operation(self)
        self.__operation_number = self.__thread.num_of_operations()
        self.__name = ""
        self.__args = list()
        self.__ignored_arg_types = (Constant,)
        self.__is_return = False
        self.__function = function
        self.__is_loop_body_operation = False  # Used generally for pthread_mutex_lock/unlock
        self.__is_if_else_block_operation = False
        self.__is_switch_case_operation = False
        self.__related_mutex = None
        self.__is_switch = False
        self.__is_case = False
        self.__switch_parent_operation = None  # It could be useful for nested switch
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
        elif isinstance(self.__node, Switch):
            self.__is_switch = True
        elif isinstance(self.__node, Case) or isinstance(self.__node, Default):
            self.__is_case = True

    def __add_resources(self, resources: list) -> None:
        """ Method extract from objects resources
        :param resources: list of objects which can contains resources
        """
        for arg in resources:
            if isinstance(arg, BinaryOp):
                self.__add_resources(arg.left)
                self.__add_resources(arg.right)
            elif isinstance(arg, StructRef):
                r = Resource(arg)
                r.add_field(arg.field.name)
                self.__args.append(r)
            else:
                self.__args.append(Resource(arg))

    @property
    def thread(self):
        """ Thread getter """
        return self.__thread

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
    def is_switch(self) -> bool:
        """ If operation is switch node than its True, other case is False
        :return: Boolean value
        """
        return self.__is_switch


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
    def is_switch_case_operation(self):
        """ Getter
        :return: Boolean value
        """
        return self.__is_switch_case_operation

    @is_switch_case_operation.setter
    def is_switch_case_operation(self, value: bool):
        """ Setter
        :param value: Boolean value
        """
        self.__is_switch_case_operation = value

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

    @property
    def is_case(self) -> bool:
        """ True if it is case or default node operation, False in other case
        :return: Boolean value
        """
        return self.__is_case

    @property
    def switch_parent_operation(self):
        """ Get parent object
        :return: Operation object
        """
        if not self.__is_case:
            raise MASCMException("Cannot get switch parent operation for operation which is not case or default!")
        return self.__switch_parent_operation

    @switch_parent_operation.setter
    def switch_parent_operation(self, parent):
        """ Setter. If function has a parent it is silently skipped
        Skipping avoid problems with overwriting parent for nested switch

        :param parent: Parent operation witch switch node!
        """
        if not self.__is_case:
            raise MASCMException("Cannot set switch parent operation for operation which is not case or default!")
        if self.__switch_parent_operation is None:
            self.__switch_parent_operation = parent

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
        elif isinstance(self.__node, (ID, BinaryOp, While)):
            return self.create_dependency_edge(resource)
        elif self.name == '&':
            return None
        return self.create_usage_edge(resource)

    def __eq__(self, other):
        return self.__thread.index == other.__thread.index and self.__operation_number == other.__operation_number

    def __repr__(self):
        return "o{},{}".format(self.__thread.index, self.__operation_number)
