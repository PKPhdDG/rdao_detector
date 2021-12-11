__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "1.1"

from contextlib import contextmanager

import time
import tracemalloc


@contextmanager
def resource_usage(doit):
    """ Measure time and memory usage """
    if doit:
        tracemalloc.start()
        start = time.time()
        yield
        end = time.time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print("=" * 60)
        print("Resource usage:")
        print("\tCurrent memory usage is {:.2f}MB".format(current / 10 ** 6))
        print("\tPeak was {:.2f}MB".format(peak / 10 ** 6))
        print("\tTime: {:.2f}s".format(end - start))
    else:
        yield


def functions_pair(arg) -> tuple:
    """ Function split arguments using coma as delimiter """
    safe_replaces = {
        "inc_op": "++",
        "dec_op": "--",
        "increment_operator": "++",
        "decrement_operator": "--"
    }
    if not arg:
        return tuple()
    result = list()
    for pair in arg.split(","):
        if pair in safe_replaces:
            result.append(safe_replaces[pair])
        else:
            result.append(pair)
    return tuple(result)