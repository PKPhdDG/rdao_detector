__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"

from pycparser.c_ast import FuncCall, Node, Return


class Operation:
    """Operation class"""
    def __init__(self, operation_obj: Node, thread):
        self.__operation_obj = operation_obj
        self.__thread = thread
        self.__thread.add_operation(self)
        self.__operation_number = self.__thread.num_of_operations()
        self.__name = ""
        self.__is_last_action = False
        if isinstance(self.__operation_obj, FuncCall):
            self.__name = self.__operation_obj.name.name
        if isinstance(self.__operation_obj, Return):
            self.__is_last_action = True

    @property
    def index(self):
        return self.__operation_number

    @property
    def name(self):
        return self.__name

    def is_last_action(self):
        return self.__is_last_action

    def __repr__(self):
        return "o{},{}".format(str(self.__thread)[1:], self.__operation_number)

    def __lt__(self, other):
        return self.__operation_number < other.__operation_number
