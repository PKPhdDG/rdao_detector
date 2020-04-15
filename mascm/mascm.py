__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.2"

from collections import defaultdict, namedtuple


class MultithreadedApplicationSourceCodeModel(namedtuple(
        'MASCM', ('threads', 'time_units', 'resources', 'operations', 'mutexes', 'edges', 'relations'))):
    """General class of multithreaded application source code model
    """
    mutex_attrs = defaultdict()

    def __repr__(self):
        result = super(MultithreadedApplicationSourceCodeModel, self).__repr__()
        split_str = "mutexes="
        result_parts = result.split(split_str)
        result_parts[0] += split_str
        result_parts[0] += "[" + ", ".join((m.model_repr() for m in self.q)) + "],"
        result_parts[1] = "],".join(result_parts[1].split("],")[1:])
        result = result_parts[0] + result_parts[1]
        return result

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

    def set_mutex_type(self, mutex_name: str, type_name: str) -> None:
        """ Method set type of mutex
        :param mutex_name: mutex name
        :param type_name: attribute name
        """
        mutex = next((m for m in self.q if m.name == mutex_name))
        mutex.set_type(self.mutex_attrs[type_name])
