__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.2"

from helpers.lock_type import LockType


class Lock:
    """ Lock class """
    def __init__(self, node, num):
        self.__type = LockType.PMD
        self.__name = node.type.declname
        self.__num = num

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

    def __repr__(self):
        return f"q{self.__num}"
