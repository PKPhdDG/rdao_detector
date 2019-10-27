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

    def __repr__(self):
        return "o{},{}".format(str(self.__thread), self.__operation_number)
