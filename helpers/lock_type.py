__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.2"

from enum import auto, Enum


class LockType(Enum):
    """ Lock type enum """
    PMN = auto()
    PME = auto()
    PMR = auto()
    PMD = PMN
