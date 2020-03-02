__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"

from collections import UserList


class TimeUnit(UserList):
    """Time unit class"""
    __number = 0

    def __init__(self, number: int):
        super(TimeUnit, self).__init__()
        self.__number = number

    def __eq__(self, other):
        return self.__number == other.__number

    def __add__(self, other: int):
        return self.__number + other
