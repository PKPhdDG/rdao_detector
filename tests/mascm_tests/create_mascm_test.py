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
from pycparser import parse_file
import unittest


class CreateMamTest(unittest.TestCase):
    project_dir = get_project_path()
    source_path_prefix = join(project_dir, "tests\\example_c_sources")
    multiple_files_app_path_prefix = join(source_path_prefix, "multiple_files_apps")

    def __test_thread_nesting(self, threads):
        main_thread, *other_threads = threads
        self.assertEqual(0, main_thread.depth, "Main thread does not have expected depth!")
        for thread in other_threads:
            self.assertEqual(1, thread.depth, "Nested thread does not have expected depth!")

    def test_single_thread_global_variable_if_statement(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], "\
                         "resources=[r1], operations=[o0,1, o0,2, o1,1, o1,2, o1,3], mutexes=[q1], "\
                         "edges=[(o0,1, o0,2), (r1, o1,1), (o1,1, o1,2), (o1,2, r1), (o1,1, o1,3), (o1,2, o1,3)], "\
                         "relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "single_thread_global_variable_if_statement.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))
            self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_single_thread_global_variable_if_else_statement(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], "\
                         "resources=[r1], operations=[o0,1, o0,2, o1,1, o1,2, o1,3, o1,4, o1,5], mutexes=[q1], "\
                         "edges=[(o0,1, o0,2), (r1, o1,1), (o1,1, o1,2), (o1,2, r1), (o1,1, o1,3), (o1,2, o1,3), "\
                         "(o1,3, o1,4), (o1,4, r1), (o1,4, o1,5)], relations=(forward=[], backward=[], "\
                         "symmetric=[]))"
        file_to_parse = "single_thread_global_variable_if_else_statement.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))
            self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_single_thread_global_variable_while_loop(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], "\
                         "resources=[r1], operations=[o0,1, o0,2, o1,1, o1,2, o1,3], mutexes=[q1], edges=[(o0,1, o0,2),"\
                         " (o1,1, o1,2), (o1,2, r1), (o1,2, o1,1), (o1,1, o1,3), (o1,2, o1,3)], relations=("\
                         "forward=[], backward=[], symmetric=[]))"
        file_to_parse = "single_thread_global_variable_while_loop.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))
            self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_two_threads_global_variable(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1, t2], time_units=[[t0], [t1, t2], "\
                         "[t0]], resources=[r1], operations=[o0,1, o0,2, o0,3, o1,1, o1,2, o1,3, o1,4, o2,1, o2,2,"\
                         " o2,3, o2,4], mutexes=[q1], edges=[(o0,1, o0,2), (o0,2, o0,3), (q1, o1,1), (o1,1, o1,2), "\
                         "(o1,2, r1), (o1,2, o1,3), (o1,3, q1), (o1,3, o1,4), (q1, o2,1), (o2,1, o2,2), (o2,2, r1), "\
                         "(o2,2, o2,3), (o2,3, q1), (o2,3, o2,4)], relations=(forward=[], backward=[],"\
                         " symmetric=[]))"
        file_to_parse = "two_threads_global_variable.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))
            self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_single_thread_do_while_loop(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], "\
                         "resources=[r1], operations=[o0,1, o0,2, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6], mutexes=[q1], "\
                         "edges=[(o0,1, o0,2), (q1, o1,1), (o1,1, o1,2), (o1,2, o1,3), (o1,3, r1), (o1,3, o1,4), "\
                         "(o1,4, o1,2), (o1,4, o1,5), (o1,5, q1), (o1,5, o1,6)], relations=(forward=[],"\
                         " backward=[], symmetric=[]))"
        file_to_parse = "single_thread_do_while_loop.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))
            self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_single_thread_operation_in_main_thread_for_loop_without_body(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t0, t1], [t0]],"\
                         " resources=[r1], operations=[o0,1, o0,2, o0,3, o1,1, o1,2, o1,3, o1,4], mutexes=[q1], "\
                         "edges=[(o0,1, o0,2), (r1, o0,2), (o0,2, o0,3), (q1, o1,1), (o1,1, o1,2), (o1,2, o1,2),"\
                         " (o1,2, o1,3), (o1,3, q1), (o1,3, o1,4)], relations=(forward=[], backward=[],"\
                         " symmetric=[]))"
        file_to_parse = "single_thread_operation_in_main_thread_for_loop_without_body.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))
            self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_single_thread_for_loop(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], "\
                         "resources=[r1, r2], operations=[o0,1, o0,2, o1,1, o1,2, o1,3, o1,4, o1,5], "\
                         "mutexes=[q1], edges=[(o0,1, o0,2), (o1,1, o1,2), (q1, o1,2), (o1,2, o1,3), "\
                         "(o1,3, r2), (o1,3, o1,4), (o1,4, q1), (o1,4, o1,1), (o1,1, o1,5), (o1,4, o1,5)], "\
                         "relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "single_thread_for_loop.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))
            self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_multiple_file_application(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], "\
                         "resources=[r1, r2], operations=[o0,1, o0,2, o1,1, o1,2, o1,3, o1,4, o1,5], "\
                         "mutexes=[q1], edges=[(o0,1, o0,2), (o1,1, o1,2), (q1, o1,2), (o1,2, o1,3), "\
                         "(o1,3, r2), (o1,3, o1,4), (o1,4, q1), (o1,4, o1,1), (o1,1, o1,5), (o1,4, o1,5)], "\
                         "relations=(forward=[], backward=[], symmetric=[]))"
        dir_path: str = join(self.multiple_files_app_path_prefix, "1")
        collected_ast = list()
        pure_files = purify_files(collect_c_project_files(dir_path))
        for pure_file in pure_files:
            collected_ast.append(parse_file(pure_file))
        result = create_mascm(deque(collected_ast))
        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))
        for pure_file in pure_files:
            remove(pure_file)

    def test_multiple_file_application_2(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1, t2], time_units=[[t0], [t1, t2], "\
                         "[t0]], resources=[r1], operations=[o0,1, o0,2, o0,3, o1,1, o1,2, o1,3, o1,4, o2,1, o2,2, "\
                         "o2,3, o2,4], mutexes=[q1], edges=[(o0,1, o0,2), (o0,2, o0,3), (q1, o1,1), (o1,1, o1,2), "\
                         "(o1,2, r1), (o1,2, o1,3), (o1,3, q1), (o1,3, o1,4), (q1, o2,1), (o2,1, o2,2), (o2,2, r1), "\
                         "(o2,2, o2,3), (o2,3, q1), (o2,3, o2,4)], relations=(forward=[], backward=[],"\
                         " symmetric=[]))"
        dir_path: str = join(self.multiple_files_app_path_prefix, "2")
        collected_ast = list()
        pure_files = purify_files(collect_c_project_files(dir_path))
        for pure_file in pure_files:
            collected_ast.append(parse_file(pure_file))
        result = create_mascm(deque(collected_ast))
        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))
        for pure_file in pure_files:
            remove(pure_file)

    def test_multiple_file_application_3(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], "\
                         "resources=[r1], operations=[o0,1, o0,2, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6], mutexes=[q1], "\
                         "edges=[(o0,1, o0,2), (q1, o1,1), (o1,1, o1,2), (o1,2, o1,3), (o1,3, r1), (o1,3, o1,4), "\
                         "(o1,4, o1,2), (o1,4, o1,5), (o1,5, q1), (o1,5, o1,6)], relations=(forward=[],"\
                         " backward=[], symmetric=[]))"
        dir_path: str = join(self.multiple_files_app_path_prefix, "3")
        collected_ast = list()
        pure_files = purify_files(collect_c_project_files(dir_path))
        for pure_file in pure_files:
            collected_ast.append(parse_file(pure_file))
        result = create_mascm(deque(collected_ast))
        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))
        for pure_file in pure_files:
            remove(pure_file)

    def test_multiple_file_application_4(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1, t2], "\
                         "time_units=[[t0], [t1], [t2], [t0]], resources=[], "\
                         "operations=[o0,1, o0,2, o1,1, o1,2, o1,3, o1,4, o2,1, o2,2, o2,3, o2,4], mutexes=[], "\
                         "edges=[(o0,1, o0,2), (o1,1, o1,2), (o1,2, o1,3), (o1,3, o1,4), "\
                         "(o2,1, o2,2), (o2,2, o2,3), (o2,3, o2,4)], relations=(forward=[], backward=[], "\
                         "symmetric=[]))"
        dir_path: str = join(self.multiple_files_app_path_prefix, "4")
        collected_ast = list()
        pure_files = purify_files(collect_c_project_files(dir_path))
        for pure_file in pure_files:
            collected_ast.append(parse_file(pure_file))
        result = create_mascm(deque(collected_ast))
        main_thread, *other_threads = result.threads
        self.assertEqual(0, main_thread.depth, "Main thread does not have expected depth!")
        for thread, depth in zip(other_threads, range(1, len(result.threads))):
            self.assertEqual(depth, thread.depth, "Nested thread does not have expected depth!")
        self.assertEqual(expected_mascm, str(result))
        for pure_file in pure_files:
            remove(pure_file)

    def test_multiple_file_application_5(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1, t2], "\
                         "time_units=[[t0], [t1], [t2, t1], [t1], [t0]], resources=[], "\
                         "operations=[o0,1, o0,2, o1,1, o1,2, o1,3, o1,4, o1,5, o2,1, o2,2, o2,3, o2,4], mutexes=[], "\
                         "edges=[(o0,1, o0,2), (o1,1, o1,2), (o1,2, o1,3), (o1,3, o1,4), (o1,4, o1,5), "\
                         "(o2,1, o2,2), (o2,2, o2,3), (o2,3, o2,4)], relations=(forward=[], backward=[],"\
                         " symmetric=[]))"
        dir_path: str = join(self.multiple_files_app_path_prefix, "5")
        collected_ast = list()
        pure_files = purify_files(collect_c_project_files(dir_path))
        for pure_file in pure_files:
            collected_ast.append(parse_file(pure_file))
        result = create_mascm(deque(collected_ast))
        main_thread, *other_threads = result.threads
        self.assertEqual(0, main_thread.depth, "Main thread does not have expected depth!")
        for thread, depth in zip(other_threads, range(1, len(result.threads))):
            self.assertEqual(depth, thread.depth, "Nested thread does not have expected depth!")
        self.assertEqual(expected_mascm, str(result))
        for pure_file in pure_files:
            remove(pure_file)

    def test_multiple_file_application_6(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1, t2, t3, t4], "\
                         "time_units=[[t0], [t1], [t2], [t3], [t4], [t0]], resources=[], "\
                         "operations=[o0,1, o0,2, o1,1, o1,2, o2,1, o2,2, o3,1, o3,2, o4,1], mutexes=[], "\
                         "edges=[(o0,1, o0,2), (o1,1, o1,2), (o2,1, o2,2), (o3,1, o3,2)], relations=("\
                         "forward=[], backward=[], symmetric=[]))"
        dir_path: str = join(self.multiple_files_app_path_prefix, "6")
        collected_ast = list()
        pure_files = purify_files(collect_c_project_files(dir_path))
        for pure_file in pure_files:
            collected_ast.append(parse_file(pure_file))
        result = create_mascm(deque(collected_ast))
        main_thread, *other_threads = result.threads
        self.assertEqual(0, main_thread.depth, "Main thread does not have expected depth!")
        for thread, depth in zip(other_threads, range(1, len(result.threads))):
            self.assertEqual(depth, thread.depth, "Nested thread does not have expected depth!")
        self.assertEqual(expected_mascm, str(result))
        for pure_file in pure_files:
            remove(pure_file)

    def test_multiple_file_application_7(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1, t2, t3, t4, t5], "\
                         "time_units=[[t0], [t1], [t2, t3], [t4], [t5], [t0]], resources=[], "\
                         "operations=[o0,1, o0,2, o1,1, o1,2, o1,3, o2,1, o2,2, o3,1, o3,2, o4,1, o5,1], "\
                         "mutexes=[], edges=[(o0,1, o0,2), (o1,1, o1,2), (o1,2, o1,3), (o2,1, o2,2), (o3,1, o3,2)], "\
                         "relations=(forward=[], backward=[], symmetric=[]))"
        dir_path: str = join(self.multiple_files_app_path_prefix, "7")
        collected_ast = list()
        pure_files = purify_files(collect_c_project_files(dir_path))
        for pure_file in pure_files:
            collected_ast.append(parse_file(pure_file))
        result = create_mascm(deque(collected_ast))
        main_thread, *other_threads = result.threads
        self.assertEqual(0, main_thread.depth, "Main thread does not have expected depth!")
        for thread, depth in zip(other_threads, [1, 2, 2, 3, 3]):
            self.assertEqual(depth, thread.depth, "Nested thread does not have expected depth!")
        self.assertEqual(expected_mascm, str(result))
        for pure_file in pure_files:
            remove(pure_file)

    def test_forward_relation(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], "\
                         "resources=[r1], operations=[o0,1, o0,2, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6, o1,7, o1,8, "\
                         "o1,9, o1,10, o1,11], mutexes=[], edges=[(o0,1, o0,2), (o1,1, o1,2), (o1,2, o1,3), "\
                         "(o1,3, o1,4), (o1,4, o1,5), (o1,5, r1), (o1,5, o1,6), (r1, o1,6), (o1,6, o1,7), (r1, o1,7), "\
                         "(o1,7, o1,8), (o1,8, o1,9), (o1,9, o1,8), (o1,8, o1,10), (o1,9, o1,10), (r1, o1,10), "\
                         "(o1,10, o1,11)], relations=(forward=[(o1,4, o1,10)], backward=[], symmetric=[]))"
        file_to_parse = "forward_relation.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))
            self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_two_forward_relation(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], "\
                         "resources=[r1, r2], operations=[o0,1, o0,2, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6, o1,7, o1,8, "\
                         "o1,9, o1,10, o1,11, o1,12, o1,13, o1,14, o1,15, o1,16, o1,17, o1,18, o1,19, o1,20, o1,21, "\
                         "o1,22], mutexes=[], edges=[(o0,1, o0,2), (o1,1, o1,2), (o1,2, o1,3), (o1,3, o1,4), "\
                         "(o1,4, o1,5), (o1,5, o1,6), (o1,6, o1,7), (o1,7, o1,8), (o1,8, r1), (o1,8, o1,9), "\
                         "(o1,9, o1,10), (o1,10, r2), (o1,10, o1,11), (r1, o1,11), (o1,11, o1,12), (r2, o1,12), "\
                         "(o1,12, o1,13), (r1, o1,13), (o1,13, o1,14), (r2, o1,14), (o1,14, o1,15), (o1,15, o1,16), "\
                         "(o1,16, o1,15), (o1,15, o1,17), (o1,16, o1,17), (o1,17, o1,18), (o1,18, o1,19), (o1,19, "\
                         "o1,18), (o1,18, o1,20), (o1,19, o1,20), (r1, o1,20), (o1,20, o1,21), (r2, o1,21), (o1,21, "\
                         "o1,22)], relations=(forward=[(o1,7, o1,20), (o1,9, o1,21)], backward=[], symmetric=[]))"
        file_to_parse = "two_forward_relation.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))
            self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_backward_relation(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], "\
                         "resources=[r1], operations=[o0,1, o0,2, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6, o1,7, o1,8, "\
                         "o1,9, o1,10, o1,11], mutexes=[], edges=[(o0,1, o0,2), (o1,1, o1,2), (o1,2, o1,3), "\
                         "(o1,3, r1), (o1,3, o1,4), (r1, o1,4), (o1,4, o1,5), (o1,5, o1,6), (o1,6, o1,7), "\
                         "(o1,7, o1,8), (o1,4, o1,9), (o1,9, o1,10), (r1, o1,10), (o1,10, o1,11)], "\
                         "relations=(forward=[], backward=[(o1,2, o1,5)], symmetric=[]))"
        file_to_parse = "backward_relation.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))
            self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))
