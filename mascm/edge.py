__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

from collections import namedtuple


class Edge(namedtuple("Pair", ["first", "second"])):
    """ Edge class """
    def __repr__(self):
        return str((self.first, self.second))

    def __lt__(self, other):
        return self.first < other.first or self.second < other.second

    def __contains__(self, item):
        return item == self.first or item == self.second
