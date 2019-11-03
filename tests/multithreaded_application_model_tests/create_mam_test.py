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
    test_source_path_prefix = "example_c_sources"

    def test_single_thread_global_variable_if_statement(self):
        expected_mam = "MultithreadedApplicationModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], resource=[r1]," \
                       " operations=[o0,1, o0,2, o1,1, o1,2, o1,3], mutexes=[q1], edges=[(o0,1, o0,2), (o1,1, o1,2)," \
                       " (o1,2, r1), (o1,1, o1,3), (o1,2, o1,3)])"
        file_to_parse = "single_thread_global_variable_if_statement.c.pure"
        ast = parse_file(join(self.test_source_path_prefix, file_to_parse), use_cpp=False)
        result = create_mam(deque([ast]))
        self.assertEqual(expected_mam, str(result))

    def test_single_thread_global_variable_if_else_statement(self):
        expected_mam = "MultithreadedApplicationModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], resource=[r1]," \
                       " operations=[o0,1, o0,2, o1,1, o1,2, o1,3, o1,4, o1,5], mutexes=[q1], edges=[(o0,1, o0,2), " \
                       "(o1,1, o1,2), (o1,2, r1), (o1,1, o1,3), (o1,2, o1,3), (o1,3, o1,4), (o1,4, r1), (o1,3, o1,5)," \
                       " (o1,4, o1,5)])"
        file_to_parse = "single_thread_global_variable_if_else_statement.c.pure"
        ast = parse_file(join(self.test_source_path_prefix, file_to_parse), use_cpp=False)
        result = create_mam(deque([ast]))
        self.assertEqual(expected_mam, str(result))

    def test_single_thread_global_variable_while_loop(self):
        expected_mam = "MultithreadedApplicationModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], resource=[r1]," \
                       " operations=[o0,1, o0,2, o1,1, o1,2, o1,3], mutexes=[q1], edges=[(o0,1, o0,2), (o1,1, o1,2)," \
                       " (o1,2, r1), (o1,2, o1,1), (o1,1, o1,3), (o1,2, o1,3)])"
        file_to_parse = "single_thread_global_variable_while_loop.c.pure"
        ast = parse_file(join(self.test_source_path_prefix, file_to_parse), use_cpp=False)
        result = create_mam(deque([ast]))
        self.assertEqual(expected_mam, str(result))

    def test_two_threads_global_variable(self):
        expected_mam = "MultithreadedApplicationModel(threads=[t0, t1, t2], time_units=[[t0], [t1, t2], [t0]], " \
                       "resource=[r1], operations=[o0,1, o0,2, o0,3, o1,1, o1,2, o1,3, o1,4, o2,1, o2,2, o2,3, o2,4]," \
                       " mutexes=[q1], edges=[(o0,1, o0,2), (o0,2, o0,3), (q1, o1,1), (o1,1, o1,2), (o1,2, r1), " \
                       "(o1,2, o1,3), (o1,3, q1), (o1,3, o1,4), (q1, o2,1), (o2,1, o2,2), (o2,2, r1), (o2,2, o2,3), " \
                       "(o2,3, q1), (o2,3, o2,4)])"
        file_to_parse = "two_threads_global_variable.c.pure"
        ast = parse_file(join(self.test_source_path_prefix, file_to_parse), use_cpp=False)
        result = create_mam(deque([ast]))
        self.assertEqual(expected_mam, str(result))

    def test_single_thread_do_while_loop(self):
        expected_mam = "MultithreadedApplicationModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], resource=[r1]," \
                       " operations=[o0,1, o0,2, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6], mutexes=[q1], " \
                       "edges=[(o0,1, o0,2), (q1, o1,1), (o1,1, o1,2), (o1,2, o1,3), (o1,3, r1), (o1,3, o1,4), " \
                       "(o1,4, o1,2), (o1,4, o1,5), (o1,5, q1), (o1,5, o1,6)])"
        file_to_parse = "single_thread_do_while_loop.c.pure"
        ast = parse_file(join(self.test_source_path_prefix, file_to_parse), use_cpp=False)
        result = create_mam(deque([ast]))
        self.assertEqual(expected_mam, str(result))

    def test_single_thread_operation_in_main_thread_for_loop_without_body(self):
        expected_mam = "MultithreadedApplicationModel(threads=[t0, t1], time_units=[[t0], [t0, t1], [t0]], " \
                       "resource=[r1], operations=[o0,1, o0,2, o0,3, o1,1, o1,2, o1,3, o1,4], mutexes=[q1], " \
                       "edges=[(o0,1, o0,2), (o0,2, o0,3), (q1, o1,1), (o1,1, o1,2), (o1,2, o1,2), (o1,2, o1,3), " \
                       "(o1,3, q1), (o1,3, o1,4)])"
        file_to_parse = "single_thread_operation_in_main_thread_for_loop_without_body.c.pure"
        ast = parse_file(join(self.test_source_path_prefix, file_to_parse), use_cpp=False)
        result = create_mam(deque([ast]))
        self.assertEqual(expected_mam, str(result))

    def test_single_thread_for_loop(self):
        expected_mam = "MultithreadedApplicationModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], " \
                       "resource=[r1, r2], operations=[o0,1, o0,2, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6, o1,7, o1,8, " \
                       "o1,9], mutexes=[q1], edges=[(o0,1, o0,2), (o1,1, o1,2), " \
                       "(o1,2, o1,3), (o1,3, o1,4), (o1,4, o1,5), (o1,5, o1,6), (q1, o1,6), (o1,6, o1,7), " \
                       "(o1,7, r2), (o1,7, o1,8), (o1,8, q1), (o1,8, o1,1), (o1,1, o1,9), (o1,8, o1,9)])"
        file_to_parse = "single_thread_for_loop.c.pure"
        ast = parse_file(join(self.test_source_path_prefix, file_to_parse), use_cpp=False)
        result = create_mam(deque([ast]))
        self.assertEqual(expected_mam, str(result))


if "__main__" == __name__:
    unittest.main()

