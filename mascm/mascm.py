__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"

from collections import namedtuple


class MultithreadedApplicationSourceCodeModel(namedtuple(
        'MASCM', ('threads', 'time_units', 'resources', 'operations', 'mutexes', 'edges', 'relations'))):
    """General class of multithreaded application source code model
    """

    def __getattr__(self, item: str):
        if item in ['t', 'u', 'r', 'o', 'q', 'f', 'b']:
            if 't' == item:
                return self.threads
            elif 'u' == item:
                return self.time_units
            elif 'r' == item:
                return self.resources
            elif 'o' == item:
                return self.operations
            elif 'q' == item:
                return self.mutexes
            elif 'f' == item:
                return self.edges
            elif 'b' == item:
                return self.relations
        return super(MultithreadedApplicationSourceCodeModel, self).__getattribute__(item)
