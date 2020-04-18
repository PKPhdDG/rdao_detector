__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.3"

import logging
from mascm.resource import Resource
from pycparser.c_ast import Constant, Decl, FuncCall, ID, Node, Return, UnaryOp
import sys


class Operation:
    """Operation class"""
    def __init__(self, operation_obj: Node, thread, thread_index: int, called_in_loop: bool):
        """Ctor
        :param operation_obj: Node obj
        :param thread: Thread object
        :param thread_index: Thread index in the mascm
        :param called_in_loop: Boolean value  which is True if operation is part of loop body
        """
        self.__operation_obj = operation_obj
        self.__thread = thread
        self.__thread_index = thread_index
        self.__thread.add_operation(self)
        self.__operation_number = self.__thread.num_of_operations()
        self.__name = ""
        self.__args = list()
        self.__ignored_arg_types = (Constant,)
        self.__is_last_action = False
        self.is_multiple_called = called_in_loop  # Used generally for pthread_mutex_lock/unlock
        if isinstance(self.__operation_obj, FuncCall):
            self.__name = self.__operation_obj.name.name
            if self.__operation_obj.args is not None:
                self.__args.extend(self.__operation_obj.args.exprs)
        elif isinstance(self.__operation_obj, UnaryOp):
            self.__name = self.__operation_obj.op
            self.__args.append(self.__operation_obj.expr)
        if isinstance(self.__operation_obj, Return):
            self.__is_last_action = True



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
        return self.__operation_obj

    def is_last_action(self) -> bool:
        """ If this is return operation this method return true
        :return: Boolean value
        """
        return self.__is_last_action

    def add_use_resource(self, resource: Resource) -> None:
        """ Method add resource to resource list """
        self.__args.append(resource.node)

    def has_func_use_the_resource(self, resource: Resource) -> bool:
        """ Method check given resource is used by operation
        :param resource: Resource object
        :return: Boolean value
        """
        for arg in self.__args:
            if isinstance(arg, ID):
                if hasattr(arg, "left") and hasattr(arg.left, "name") and resource.has_name(arg.left.name):
                    return True
                elif hasattr(arg, "name") and resource.has_name(arg.name):
                    return True
            elif isinstance(arg, Decl) and hasattr(arg, "name"):
                if resource.has_name(arg.name):
                    return True
            else:
                if not isinstance(arg, self.__ignored_arg_types):
                    logging.warning(f"Cannot handle arg: {arg}")
        return False

    def is_operation_of_thread(self, other_thread) -> bool:
        """ Method check operation is operation of a given thread """
        return self.__thread == other_thread

    def __repr__(self):
        return "o{},{}".format(self.__thread_index, self.__operation_number)

    def __lt__(self, other):
        return self.__operation_number < other.__operation_number
