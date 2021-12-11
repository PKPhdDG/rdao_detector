__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "1.1"

from enum import auto, Enum


class EdgeType(Enum):
    """ Edge type enum """
    transition = auto()
    usage = auto()
    dependency = auto()
    locking = auto()
    unlocking = auto()
