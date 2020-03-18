__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.2"


class Edge:
    """ Edge class """
    def __init__(self, first, second):
        self.__first = first
        self.__second = second

    def __repr__(self):
        return str((self.__first, self.__second))

    def __lt__(self, other):
        return self.__first < other.__first or self.__second < other.__second
