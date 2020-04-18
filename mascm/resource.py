__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.3"

from pycparser.c_ast import Node


class Resource:
    """ Resource class """
    def __init__(self, node, num: int):
        self.__node = node
        self.__names = {node.name}
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

    @property
    def node(self) -> Node:
        """ Node obj getter """
        return self.__node

    def __hash__(self):
        return hash(self.__node)

    def __lt__(self, other):
        return self.__num < other.__num

    def __eq__(self, other):
        if isinstance(other, Resource):
            return other.__names == self.__names
        return False

    def __repr__(self):
        return f"r{self.__num}"

    def __contains__(self, item):
        return item in self.__names
