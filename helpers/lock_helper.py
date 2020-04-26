__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

import config as c
from helpers.lock_type import LockType

lock_types_str = {
    LockType.PMN: "PTHREAD_MUTEX_NORMAL",
    LockType.PME: "PTHREAD_MUTEX_ERRORCHECK",
    LockType.PMR: "PTHREAD_MUTEX_RECURSIVE",
    LockType.PMD: "PTHREAD_MUTEX_DEFAULT"
}

lock_strings = {
    "PTHREAD_MUTEX_NORMAL": LockType.PMN,
    "PTHREAD_MUTEX_ERRORCHECK": LockType.PME,
    "PTHREAD_MUTEX_RECURSIVE": LockType.PMR,
}
lock_strings["PTHREAD_MUTEX_DEFAULT"] = lock_strings[c.PTHREAD_MUTEX_DEFAULT_VAL]
