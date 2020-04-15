__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.3"

from mascm.operation import Operation
from mascm.time_unit import TimeUnit
from pycparser.c_ast import ExprList
from typing import Optional


class Thread:
    """Thread representation object
    """
    def __init__(self, thread_index: int, expr_list: Optional[ExprList], time_unit: TimeUnit, depth: int = 0):
        """C'tor
        :param expr_list: ExprList object
        :param time_unit: Time unit in which thread works
        :param depth: Value increase when thread is nested
        """
        self.__name = expr_list.exprs[0].expr.name if expr_list is not None else "t0"
        self.__args = expr_list
        self.__time_unit = time_unit
        self.__operations = list()
        self.__depth = depth
        self.__thread_index = thread_index
        self.__thread_does_not_care_about_anything = False

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
    def time_unit(self):
        """ Getter
        :return: Time unit
        """
        return self.__time_unit

    @time_unit.setter
    def time_unit(self, new_time_unit):
        self.__time_unit = new_time_unit

    @property
    def depth(self):
        """ Getter
        :return: Depth value
        """
        return self.__depth

    def set_always_parallel(self):
        """ Mark thread as always parallel """
        self.__thread_does_not_care_about_anything = True

    def is_always_parallel(self):
        """ Method return True value if thread is always parallel
        :return: Boolean value
        """
        return self.__thread_does_not_care_about_anything

    def __repr__(self) -> str:
        return f"t{self.__thread_index}"

    def __eq__(self, other) -> bool:
        return (self.__name == other.__name) and (self.__thread_index == other.__thread_index)
