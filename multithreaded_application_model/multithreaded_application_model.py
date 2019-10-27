__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"


from collections import namedtuple
from multithreaded_application_model.thread import Thread
from multithreaded_application_model.time_unit import TimeUnit
from pycparser.c_ast import FuncCall, FuncDef


class MultithreadedApplicationModel(namedtuple(
    'MAM', ('threads', 'time_units', 'resource', 'operations', 'mutexes', 'edges'))):
    """General class of multithreaded application model
    """
    __declared_functions = dict()
    __time_unit_number = 0
    __new_time_unit = True

    def __getattr__(self, item):
        if item in ['t', 'u', 'r', 'o', 'q', 'f']:
            if 't' == item: return self.threads
            elif 'u' == item: return self.time_units
            elif 'r' == item: return self.resource
            elif 'o' == item: return self.operations
            elif 'q' == item: return self.mutexes
            elif 'f' == item: return self.edges
        return super(MultithreadedApplicationModel, self).__getattr__(item)

    def __add_mutex_to_mam(self, node) -> None:
        """Convert AST node to mutex into MultithreadedApplicationModel notation
        :param node: AST Node
        """
        self.q.add((node.type.declname, 'PMD'))

    def __parse_function(self, node:FuncDef):
        if hasattr(node, 'decl') and hasattr(node.decl, 'name') and "main" == node.decl.name:
            self.__parse_function_main(node)

    def __parse_function_call(self, node: FuncCall):
        if 'pthread_create' == node.name.name:
            self.__parse_function_call_pthread_create(node)
        elif 'pthread_join' == node.name.name:
            self.__new_time_unit = True

    def __parse_function_call_pthread_create(self, node: FuncCall):
        if self.__new_time_unit:
            self.__time_unit_number += 1
            self.__new_time_unit = False
            self.u.append(TimeUnit(self.__time_unit_number))
        thread = Thread(node.args, self.__time_unit_number)
        self.t.append(thread)
        self.u[-1].append(thread)

    def __parse_function_main(self, node: FuncDef):
        self.__put_main_thread_to_model()
        for node in node.body:
            if isinstance(node, FuncCall):
                self.__parse_function_call(node)

    def __put_main_thread_to_model(self):
        thread = Thread(None, 0)
        unit = TimeUnit(0)
        unit.append(thread)
        if not thread in self.t:
            self.t.append(thread)
        self.u.append(unit)

    def add_declared_function(self, node):
        self.__declared_functions[node.decl.name] = node

    @staticmethod
    def create_multithreaded_application_model(ast):
        mam = MultithreadedApplicationModel(list(), list(), set(), set(), set(), set())

        for node in ast:
            if hasattr(node, 'storage') and ("typedef" in node.storage):
                continue
            elif hasattr(node, 'type') and hasattr(node.type, 'type'):
                if hasattr(node.type.type, 'names') and "pthread_mutex_t" in node.type.type.names:
                    mam.__add_mutex_to_mam(node)
            elif isinstance(node, FuncDef):
                mam.add_declared_function(node)
                mam.__parse_function(node)
        mam.__put_main_thread_to_model()
        return mam
