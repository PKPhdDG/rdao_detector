__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"

from collections import deque
from multithreaded_application_model import create_multithreaded_application_model as create_mam
from os.path import join
from pycparser import parse_file
import unittest


class CreateMamTest(unittest.TestCase):
    test_source_path_prefix = "example_c_sources/"

    def test_single_thread_global_variable_if_statement(self):
        expected_mam = "MultithreadedApplicationModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], resource=[r1]," \
                       " operations=[o0,1, o0,2, o1,1, o1,2, o1,3], mutexes=[q1], edges=[(o0,1, o0,2), (o1,1, o1,2)," \
                       " (o1,1, o1,3), (o1,2, o1,3)])"
        file_to_parse = "single_thread_global_variable_if_statement.c.pure"
        ast = parse_file(join(self.test_source_path_prefix, file_to_parse), use_cpp=False)
        result = create_mam(deque([ast]))
        self.assertEqual(expected_mam, str(result))


if "__main__" == __name__:
    unittest.main()

