__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"

from collections import namedtuple
from multithreaded_application_model.thread import Thread
from multithreaded_application_model.time_unit import TimeUnit
from parsing_utils import Function
from pycparser.c_ast import FuncDef
import sys


class MultithreadedApplicationModel(namedtuple(
    'MAM', ('threads', 'time_units', 'resource', 'operations', 'mutexes', 'edges'))):
    """General class of multithreaded application model
    """
    __declared_functions = list()
    time_unit_number = 0
    new_time_unit = True

    def __getattr__(self, item):
        if item in ['t', 'u', 'r', 'o', 'q', 'f']:
            if 't' == item:
                return self.threads
            elif 'u' == item:
                return self.time_units
            elif 'r' == item:
                return self.resource
            elif 'o' == item:
                return self.operations
            elif 'q' == item:
                return self.mutexes
            elif 'f' == item:
                return self.edges
        return super(MultithreadedApplicationModel, self).__getattribute__(item)

    def __add_mutex_to_mam(self, node) -> None:
        """Convert AST node to mutex into MultithreadedApplicationModel notation
        :param node: AST Node
        """
        self.q.add((node.type.declname, 'PMD'))

    def add_declared_function(self, node):
        self.__declared_functions.append(node)

    def __put_main_thread_to_model(self):
        thread = Thread(None, 0)
        unit = TimeUnit(0)
        unit.append(thread)
        if thread not in self.t:
            self.t.append(thread)
        self.u.append(unit)

    def parse_functions(self):
        for function in self.__declared_functions:
            function.parse_function()

    @staticmethod
    def create_multithreaded_application_model(ast):
        mam = MultithreadedApplicationModel(list(), list(), set(), list(), set(), set())
        mam.__put_main_thread_to_model()
        for node in ast:
            if hasattr(node, 'storage') and ("typedef" in node.storage):
                continue
            elif hasattr(node, 'type') and hasattr(node.type, 'type'):
                if hasattr(node.type.type, 'names') and "pthread_mutex_t" in node.type.type.names:
                    mam.__add_mutex_to_mam(node)
            elif isinstance(node, FuncDef):
                mam.add_declared_function(Function(node, mam))
            else:
                print(node, "is not expected", file=sys.stderr)

        mam.parse_functions()
        if len(mam.u) > 1:
            mam.__put_main_thread_to_model()
        return mam
