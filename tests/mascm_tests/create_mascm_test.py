__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"

from collections import deque
from helpers.path import collect_c_project_files, get_project_path
from helpers.purifier import purify, purify_files
from mascm import create_mascm
from os import remove
from os.path import join
from pathlib import Path
from pycparser import parse_file
import unittest


class CreateMamTest(unittest.TestCase):
    project_dir = get_project_path()
    source_path_prefix = join(project_dir, "tests\example_c_sources")
    multiple_files_app_path_prefix = join(source_path_prefix, "multiple_files_apps")

    def test_single_thread_global_variable_if_statement(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], " \
                       "resource=[r1], operations=[o0,1, o0,2, o1,1, o1,2, o1,3], mutexes=[q1], edges=[(o0,1, o0,2), " \
                       "(o1,1, o1,2), (o1,2, r1), (o1,1, o1,3), (o1,2, o1,3)])"
        file_to_parse = "single_thread_global_variable_if_statement.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path, use_cpp=False)
            result = create_mascm(deque([ast]))
        self.assertEqual(expected_mascm, str(result))

    def test_single_thread_global_variable_if_else_statement(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], " \
                       "resource=[r1], operations=[o0,1, o0,2, o1,1, o1,2, o1,3, o1,4, o1,5], mutexes=[q1], " \
                       "edges=[(o0,1, o0,2), (o1,1, o1,2), (o1,2, r1), (o1,1, o1,3), (o1,2, o1,3), (o1,3, o1,4), " \
                       "(o1,4, r1), (o1,3, o1,5), (o1,4, o1,5)])"
        file_to_parse = "single_thread_global_variable_if_else_statement.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path, use_cpp=False)
            result = create_mascm(deque([ast]))
        self.assertEqual(expected_mascm, str(result))

    def test_single_thread_global_variable_while_loop(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], " \
                       "resource=[r1], operations=[o0,1, o0,2, o1,1, o1,2, o1,3], mutexes=[q1], edges=[(o0,1, o0,2), " \
                       "(o1,1, o1,2), (o1,2, r1), (o1,2, o1,1), (o1,1, o1,3), (o1,2, o1,3)])"
        file_to_parse = "single_thread_global_variable_while_loop.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path, use_cpp=False)
            result = create_mascm(deque([ast]))
        self.assertEqual(expected_mascm, str(result))

    def test_two_threads_global_variable(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1, t2], time_units=[[t0], [t1, t2], " \
                       "[t0]], resource=[r1], operations=[o0,1, o0,2, o0,3, o1,1, o1,2, o1,3, o1,4, o2,1, o2,2, o2,3," \
                       " o2,4], mutexes=[q1], edges=[(o0,1, o0,2), (o0,2, o0,3), (q1, o1,1), (o1,1, o1,2), " \
                       "(o1,2, r1), (o1,2, o1,3), (o1,3, q1), (o1,3, o1,4), (q1, o2,1), (o2,1, o2,2), (o2,2, r1), " \
                       "(o2,2, o2,3), (o2,3, q1), (o2,3, o2,4)])"
        file_to_parse = "two_threads_global_variable.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path, use_cpp=False)
            result = create_mascm(deque([ast]))
        self.assertEqual(expected_mascm, str(result))

    def test_single_thread_do_while_loop(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], " \
                       "resource=[r1], operations=[o0,1, o0,2, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6], mutexes=[q1], " \
                       "edges=[(o0,1, o0,2), (q1, o1,1), (o1,1, o1,2), (o1,2, o1,3), (o1,3, r1), (o1,3, o1,4), " \
                       "(o1,4, o1,2), (o1,4, o1,5), (o1,5, q1), (o1,5, o1,6)])"
        file_to_parse = "single_thread_do_while_loop.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path, use_cpp=False)
            result = create_mascm(deque([ast]))
        self.assertEqual(expected_mascm, str(result))

    def test_single_thread_operation_in_main_thread_for_loop_without_body(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t0, t1], [t0]], " \
                       "resource=[r1], operations=[o0,1, o0,2, o0,3, o1,1, o1,2, o1,3, o1,4], mutexes=[q1], " \
                       "edges=[(o0,1, o0,2), (r1, o0,2), (o0,2, o0,3), (q1, o1,1), (o1,1, o1,2), (o1,2, o1,2)," \
                       " (o1,2, o1,3), (o1,3, q1), (o1,3, o1,4)])"
        file_to_parse = "single_thread_operation_in_main_thread_for_loop_without_body.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path, use_cpp=False)
            result = create_mascm(deque([ast]))
        self.assertEqual(expected_mascm, str(result))

    def test_single_thread_for_loop(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], " \
                       "resource=[r1, r2], operations=[o0,1, o0,2, o1,1, o1,2, o1,3, o1,4, o1,5], " \
                       "mutexes=[q1], edges=[(o0,1, o0,2), (o1,1, o1,2), (q1, o1,2), (o1,2, o1,3), " \
                       "(o1,3, r2), (o1,3, o1,4), (o1,4, q1), (o1,4, o1,1), (o1,1, o1,5), (o1,4, o1,5)])"
        file_to_parse = "single_thread_for_loop.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path, use_cpp=False)
            result = create_mascm(deque([ast]))
        self.assertEqual(expected_mascm, str(result))

    def test_multiple_file_application(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], " \
                       "resource=[r1, r2], operations=[o0,1, o0,2, o1,1, o1,2, o1,3, o1,4, o1,5], " \
                       "mutexes=[q1], edges=[(o0,1, o0,2), (o1,1, o1,2), (q1, o1,2), (o1,2, o1,3), " \
                       "(o1,3, r2), (o1,3, o1,4), (o1,4, q1), (o1,4, o1,1), (o1,1, o1,5), (o1,4, o1,5)])"
        dir_path: str = join(self.multiple_files_app_path_prefix, "1")
        collected_ast = list()
        pure_files = purify_files(collect_c_project_files(dir_path))
        for pure_file in pure_files:
            collected_ast.append(parse_file(pure_file))
        result = create_mascm(deque(collected_ast))
        self.assertEqual(expected_mascm, str(result))
        for pure_file in pure_files:
            remove(pure_file)


if "__main__" == __name__:
    unittest.main()
