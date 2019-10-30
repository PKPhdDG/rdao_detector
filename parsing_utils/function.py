__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"

from collections import deque
from multithreaded_application_model.operation import Operation
from multithreaded_application_model.thread import Thread
from multithreaded_application_model.time_unit import TimeUnit
from pycparser.c_ast import FuncDef, FuncCall
import sys


class Function:
    def __init__(self, node: FuncDef):
        self.__node = node

    @property
    def body(self):
        return self.__node.body

    @property
    def name(self):
        return self.__node.decl.name
