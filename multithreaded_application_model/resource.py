__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"


class Resource:
    def __init__(self, node, num, *args):
        self.__node = node
        self.__names = set(args)
        self.__num = num

    def add_name(self, name):
        self.__names.add(name)

    def __eq__(self, other):
        return other.__names == self.__names

    def __repr__(self):
        return f"r{self.__num}"

    def __contains__(self, item):
        return item in self.__names
