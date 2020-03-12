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
        """ Operation index """
        return self.__operation_number

    @property
    def name(self) -> str:
        """ Name of operation if this is function call. In other case name is empty.
        :return: String value
        """
        return self.__name

    def is_last_action(self) -> bool:
        """ If this is return operation this method return true
        :return: Boolean value
        """
        return self.__is_last_action

    def __repr__(self):
        return "o{},{}".format(str(self.__thread)[1:], self.__operation_number)

    def __lt__(self, other):
        return self.__operation_number < other.__operation_number
