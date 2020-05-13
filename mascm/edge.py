__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

from collections import namedtuple
from helpers.exceptions import MASCMException
from helpers import EdgeType


class Edge(namedtuple("Pair", ["first", "second"])):
    """ Edge class """
    @property
    def edge_type(self):
        """ Edge type property """
        # Inline imports to avoid circular dependencies
        from mascm.lock import Lock
        from mascm.operation import Operation
        from mascm.resource import Resource
        if isinstance(self.first, Operation) and isinstance(self.second, Operation):
            return EdgeType.transition
        elif isinstance(self.first, Operation) and isinstance(self.second, Resource):
            return EdgeType.usage
        elif isinstance(self.first, Resource) and isinstance(self.second, Operation):
            return EdgeType.dependency
        elif isinstance(self.first, Lock) and isinstance(self.second, Operation):
            return EdgeType.locking
        elif isinstance(self.first, Operation) and isinstance(self.second, Lock):
            return EdgeType.unlocking
        raise MASCMException(f"Unknown type of edge: {self}")

    def __repr__(self):
        return str((self.first, self.second))

    def __eq__(self, other):
        return (self.edge_type == other.edge_type) and (self.first == other.first) and (self.second == other.second)
