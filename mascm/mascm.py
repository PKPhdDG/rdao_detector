__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"

from collections import namedtuple


class MultithreadedApplicationSourceCodeModel(namedtuple(
        'MASCM', ('threads', 'time_units', 'resource', 'operations', 'mutexes', 'edges'))):
    """General class of multithreaded application source code model
    """

    def __getattr__(self, item: str):
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
        return super(MultithreadedApplicationSourceCodeModel, self).__getattribute__(item)
