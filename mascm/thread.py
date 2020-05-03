__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

from mascm.operation import Operation
from mascm.time_unit import TimeUnit
from pycparser.c_ast import ExprList
from typing import Optional


class Thread:
    """Thread representation object
    """
    def __init__(self, thread_index: int, expr_list: Optional[ExprList], depth: int = 0):
        """C'tor
        :param expr_list: ExprList object
        :param time_unit: Time unit in which thread works
        :param depth: Value increase when thread is nested
        """
        self.__name = expr_list.exprs[0].expr.name if expr_list is not None else "t0"
        self.__args = expr_list
        self.__operations = list()
        self.__depth = depth
        self.__thread_index = thread_index
        self.time_units = list()

    def add_operation(self, operation: Operation):
        """ Add operation which is run in this thread
        :param operation: Operation object
        """
        self.__operations.append(operation)

    def num_of_operations(self) -> int:
        """ Getter
        :return: Number of operations in thread
        """
        return len(self.__operations)

    @property
    def index(self):
        """ Getter
        :return: index
        """
        return self.__thread_index

    @property
    def depth(self):
        """ Getter
        :return: Depth value
        """
        return self.__depth

    @property
    def operations(self):
        """ Getter
        :return: Operations
        """
        return self.__operations

    def __repr__(self) -> str:
        return f"t{self.__thread_index}"

    def __eq__(self, other) -> bool:
        return (self.__name == other.__name) and (self.__thread_index == other.__thread_index)
