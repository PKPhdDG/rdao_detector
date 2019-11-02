__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"


class Operation:
    def __init__(self, operation_obj, thread):
        self.__operation_obj = operation_obj
        self.__thread = thread
        self.__thread.add_operation(self)
        self.__operation_number = self.__thread.num_of_operations()

    @property
    def index(self):
        return self.__operation_number

    def __repr__(self):
        return "o{},{}".format(str(self.__thread)[1:], self.__operation_number)

    def __lt__(self, other):
        return self.__operation_number < other.__operation_number
