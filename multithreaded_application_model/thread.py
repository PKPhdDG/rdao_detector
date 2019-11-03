__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"

from multithreaded_application_model.operation import Operation
from multithreaded_application_model.time_unit import TimeUnit
from pycparser.c_ast import ExprList


class Thread:
    """Thread representation object
    """
    def __init__(self, expr_list: ExprList, time_unit: TimeUnit):
        """C'tor
        :param name: Thread name
        :param expr_list: ExprList object
        """
        self.__name = expr_list.exprs[0].expr.name if expr_list is not None else "t0"
        self.__args = expr_list
        self.__time_unit = time_unit
        self.__operations = list()

    def add_operation(self, operation: Operation):
        self.__operations.append(operation)

    def num_of_operations(self) -> int:
        return len(self.__operations)

    @property
    def time_unit(self):
        return self.__time_unit

    @time_unit.setter
    def time_unit(self, new_time_unit):
        self.__time_unit = new_time_unit

    def __repr__(self) -> str:
        return self.__name

    def __eq__(self, other) -> bool:
        return self.__name == other.__name
