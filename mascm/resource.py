__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

from sortedcontainers import SortedSet
from helpers.exceptions import MASCMException
from helpers.mascm_helper import extract_resource_name, extract_resource_type
from pycparser.c_ast import *
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

        self.__type, self.__is_struct = extract_resource_type(node)
        self.__fields = []  # For structure

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

    def add_fields(self, node: Struct):
        """ Method add fields from Struct node """
        for decl in node.decls:
            self.__fields.append(decl.name)

    def add_field(self, name: str):
        """ Method to add single field name """
        self.__fields.append(name)

    @property
    def is_struct(self) -> bool:
        """ To check resource is struct """
        return self.__is_struct

    @property
    def names(self) -> set:
        """ All names getter """
        return self.__names

    @property
    def node(self) -> Node:
        """ Node obj getter """
        return self.__node

    @property
    def type(self) -> str:
        """ Type name """
        return self.__type

    def model_repr(self) -> str:
        """ Return model representation """
        template = "{names}"
        if not self.__fields:
            return "{" + template.format(names=", ".join(SortedSet(self.__names))) + "}"
        n = self.names
        for name in self.names:
            for field in self.__fields:
                n.add(f"{name}.{field}")
        return "{" + template.format(names=", ".join(SortedSet(self.__names))) + "}"

    def __hash__(self):
        return hash(self.__node)

    def __eq__(self, other):
        if isinstance(other, Resource):
            return other.__names == self.__names
        return False

    def __repr__(self):
        return f"r{self.__num}"

    def __contains__(self, item):
        if item is None:
            return False

        if '.' not in item:
            return item in self.__names

        name, field = item.split('.')
        return (name in self.__names) and (field in self.__fields)
