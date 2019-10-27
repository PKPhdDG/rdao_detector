__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"


from pycparser.c_ast import ExprList


class Thread:
    """Thread representation object
    """
    def __init__(self, expr_list: ExprList, time_unit: int):
        """C'tor
        :param name: Thread name
        :param expr_list: ExprList object
        """
        self.__name = expr_list.exprs[0].expr.name if expr_list is not None else "t0"
        self.__args = expr_list
        self.__time_unit = time_unit

    def __repr__(self):
        return self.__name

    def __eq__(self, other):
        return self.__name == other.__name
