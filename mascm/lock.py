__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.2"

from enum import Enum


class LockType(Enum):
    PMN = 1
    PME = 2
    PMR = 3
    PMD = 1


class Lock:
    def __init__(self, node, num):
        self.__type = LockType.PMD
        self.__name = node.type.declname
        self.__num = num

    @property
    def name(self):
        return self.__name

    def __repr__(self):
        return f"q{self.__num}"
