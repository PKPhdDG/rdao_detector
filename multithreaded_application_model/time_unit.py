__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"

from collections import UserList


class TimeUnit(UserList):
    __number = 0

    def __init__(self, number):
        super(TimeUnit, self).__init__()
        self.__number = number
