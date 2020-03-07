__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"

from collections import namedtuple


class Relations(namedtuple('RelationSet', ('forward', 'backward', 'symmetric'), defaults=[[], [], []])):
    """Class is container of relations"""

    def __repr__(self):
        return super(Relations, self).__repr__()
