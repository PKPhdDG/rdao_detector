__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "1.1"

from collections import defaultdict, namedtuple
from typing import Sequence


class MultithreadedApplicationSourceCodeModel(namedtuple(
        'MASCM', ('threads', 'time_units', 'resources', 'operations', 'mutexes', 'edges', 'relations'))):
    """General class of multithreaded application source code model
    """
    mutex_attrs = defaultdict()
    local_resources = list()
    struct_defs = list()

    def __prepare_visual_fix(self, model: str, model_set: str, elements: Sequence) -> str:
        """ Function applied fixes for specified elements of model
        :param model: model as a string
        :param model_set: Set of model which should be replaced
        :param elements: Sequence with elements for changing representation
        :return:
        """
        model_set += "="
        result_parts = model.split(model_set)
        result_parts[0] += model_set
        result_parts[0] += "[" + ", ".join((m.model_repr() for m in elements)) + "],"
        result_parts[1] = "],".join(result_parts[1].split("],")[1:])
        model = result_parts[0] + result_parts[1]
        return model

    def __repr__(self):
        result = super(MultithreadedApplicationSourceCodeModel, self).__repr__()
        if self.mutexes:
            result = self.__prepare_visual_fix(result, "mutexes", self.mutexes)
        if self.resources:
            result = self.__prepare_visual_fix(result, "resources", self.resources)
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
