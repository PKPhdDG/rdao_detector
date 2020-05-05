__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

from helpers.exceptions import MASCMException
from helpers.mascm_helper import extract_resource_name
from pycparser.c_ast import Node
from typing import Optional


class Resource:
    """ Resource class """
    def __init__(self, node, num: int = -1, names: Optional[set] = None):
        """ Ctor
        :param node: Node from code
        :param num: order number of resource if share, in other case -1
        """
        self.__node = node
        self.__names = {extract_resource_name(node)}
        if names is not None:
            self.__names.update(names)
        self.__num = num

    def add_name(self, name: str):
        """ Add resource name or resource alias
        :param name: String with name
        """
        self.__names.add(name)

    def has_names(self, names) -> bool:
        """ Resource has given name or alias
        :param names: Set of resource names
        :return: Boolean value with result
        """
        return names == self.__names

    def set_index(self, index):
        """ Set resource index
        If resource is local resource

        :param index: Int value
        """
        if self.__num > 0:
            raise MASCMException("Cannot change index of resource if resource has positive index")
        self.__num = index

    def get_resource_names_set(self) -> set:
        """ Method return set of names
        :return: Set
        """
        return self.__names

    # @property
    # def name(self) -> str:
    #     """ Getter return name if resource is argument """
    #     return next(iter(self.__names))

    @property
    def names(self) -> set:
        """ All names getter """
        return self.__names

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
