__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

from pycparser.c_ast import FuncDef


class Function:
    """ Function object"""

    def __init__(self, node: FuncDef):
        self.__node = node

    @property
    def node(self):
        return self.__node

    @property
    def body(self):
        return self.__node.body

    @property
    def name(self):
        return self.__node.decl.name
