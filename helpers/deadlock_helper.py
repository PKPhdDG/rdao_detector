__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.2"

from helpers.deadlock_type import DeadlockType

deadlock_causes_str = {
    DeadlockType.double_lock: "Pair of mutexes are mutually exclusive",
    DeadlockType.missing_unlock: "Mutex is not released",
    DeadlockType.incorrect_lock_type: "Incorrect type of mutex",
}
