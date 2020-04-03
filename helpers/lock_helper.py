__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.2"

from mascm import LockType

lock_types_str = {
    LockType.PMN: "PTHREAD_MUTEX_NORMAL",
    LockType.PME: "PTHREAD_MUTEX_ERRORCHECK",
    LockType.PMR: "PTHREAD_MUTEX_RECURSIVE",
    LockType.PMD: "PTHREAD_MUTEX_DEFAULT"
}
