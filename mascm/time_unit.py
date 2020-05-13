__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

from collections import UserList


class TimeUnit(UserList):
    """Time unit class"""
    __number = 0

    def __init__(self):
        super(TimeUnit, self).__init__()
        self.number = 0

    def __add__(self, other: int) -> int:
        return self.number + other
