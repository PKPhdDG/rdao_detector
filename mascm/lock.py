__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "1.1"

from helpers.lock_helper import lock_strings
from helpers.lock_type import LockType
import typing


class Lock:
    """ Lock class """
    def __init__(self, node, num, struct_name: typing.Optional[str] = None):
        self.__type = LockType.PMD
        try:
            self.__name = node.type.declname
        except AttributeError:
            self.__name = node.name
        self.__num = num
        self.__struct_name = struct_name

    @property
    def struct_name(self) -> str:
        """ Struct name getter
        :return: str with struct name
        """
        return self.__struct_name

    @property
    def name(self) -> str:
        """ Name getter
        :return: str with name
        """
        return self.__name

    @property
    def index(self) -> int:
        """ Lock index
        :return: int
        """
        return self.__num

    @property
    def type(self) -> LockType:
        """ Mutex type
        :return:
        """
        return self.__type

    def set_type(self, type_str: str) -> None:
        """ Method set lock type using string
        :param type_str: String with type
        """
        self.__type = lock_strings[type_str]

    def model_repr(self) -> str:
        """ Function build string for model representation """
        type_str = str(self.type).split(".")[1]
        return f"({self.name}, {type_str})"

    def compare(self, other):
        """ Function created for comparing because overriding __eq__ make Locks unhashable """
        return (self.name == other.name) and (self.type == other.type) and (self.index == other.index)

    def __repr__(self):
        return f"q{self.__num}"
