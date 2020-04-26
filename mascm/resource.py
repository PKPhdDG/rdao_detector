__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

from helpers.exceptions import MASCMException
from helpers.mascm_helper import extract_resource_name
from pycparser.c_ast import Node


class Resource:
    """ Resource class """
    def __init__(self, node, num: int = -1):
        """ Ctor
        :param node: Node from code
        :param num: order number of resource if share, in other case -1
        """
        self.__node = node
        self.__names = {extract_resource_name(node)}
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

    def get_resource_names_set(self) -> set:
        """ Method return set of names
        :return: Set
        """
        return self.__names

    @property
    def name(self) -> str:
        """ Getter return name if resource is argument """
        return next(iter(self.__names))

    @property
    def node(self) -> Node:
        """ Node obj getter """
        return self.__node

    def __hash__(self):
        return hash(self.__node)

    def __eq__(self, other):
        if isinstance(other, Resource):
            return other.__names == self.__names
        return False

    def __repr__(self):
        return f"r{self.__num}"

    def __contains__(self, item):
        return item in self.__names
