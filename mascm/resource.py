__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.2"

from pycparser.c_ast import Node


class Resource:
    """ Resource class """
    def __init__(self, node, num: int, *args):
        self.__node = node
        self.__names = set(args)
        self.__num = num

    def add_name(self, name: str):
        """ Add resource name or resource alias
        :param name: String with name
        """
        self.__names.add(name)

    def has_name(self, name) -> bool:
        """ Resource has given name or alias
        :param name: String with name
        :return: Boolean value with result
        """
        return name in self.__names

    def get_node(self) -> Node:
        """ Method return Node obj """
        return self.__node

    def __eq__(self, other):
        return other.__names == self.__names

    def __repr__(self):
        return f"r{self.__num}"

    def __contains__(self, item):
        return item in self.__names
