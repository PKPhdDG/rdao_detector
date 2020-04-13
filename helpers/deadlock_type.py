#!/usr/bin/env python3.7

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.2"

from enum import auto, Enum


class DeadlockType(Enum):
    """ Enum which help differentiate between the cause of deadlock """
    exclusion_lock = auto()
    double_lock = auto()
    missing_unlock = auto()
    incorrect_lock_type = auto()
