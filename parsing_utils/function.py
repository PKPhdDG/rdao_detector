__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"

from multithreaded_application_model.operation import Operation
from multithreaded_application_model.thread import Thread
from multithreaded_application_model.time_unit import TimeUnit
from pycparser.c_ast import FuncDef, FuncCall
import sys


class Function:
    __time_unit_number = 0
    __new_time_unit = True

    def __init__(self, node: FuncDef, multithreaded_application_model):
        self.__node = node
        self.__mam = multithreaded_application_model

    def parse_function(self):
        for node in self.__node.body:
            if isinstance(node, FuncCall):
                self.__parse_function_call(node)
            else:
                operation = Operation(node, self.__mam.t[-1])
                self.__mam.o.append(operation)

    def __parse_function_call(self, node: FuncCall):
        if 'pthread_create' == node.name.name:
            self.__parse_function_call_pthread_create(node)
        elif 'pthread_join' == node.name.name:
            self.__parse_function_call_pthread_join(node)
        else:
            print("Call unknown function:", node, file=sys.stderr)

    def __parse_function_call_pthread_create(self, node: FuncCall):
        if self.__new_time_unit:
            self.__mam.time_unit_number += 1
            self.__mam.new_time_unit = False
            self.__mam.u.append(TimeUnit(self.__mam.time_unit_number))
        thread = Thread(node.args, self.__mam.time_unit_number)
        self.__mam.t.append(thread)
        self.__mam.u[-1].append(thread)

    def __parse_function_call_pthread_join(self, node: FuncCall):
        self.__new_time_unit = True
