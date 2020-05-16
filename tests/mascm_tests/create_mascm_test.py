#!/usr/bin/env python3.8

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

from collections import deque
import config as c
from helpers.path import collect_c_project_files
from helpers.purifier import purify, purify_files
from mascm import create_mascm
from os import remove
from os.path import join
from pycparser import parse_file
from tests.test_base import TestBase
import unittest


class CreateMamTest(unittest.TestCase, TestBase):
    def __test_thread_nesting(self, threads):
        main_thread, *other_threads = threads
        self.assertEqual(0, main_thread.depth, "Main thread does not have expected depth!")
        for thread in other_threads:
            self.assertEqual(1, thread.depth, "Nested thread does not have expected depth!")

    @staticmethod
    def _print_nodes(operations: list):
        for o in operations:
            print(o, str(o.node).replace("\n", ''))

    def tearDown(self) -> None:
        """ Cleanup after test """
        super(CreateMamTest, self).tearDown()
        c.relations["forward"] = []
        c.relations["backward"] = []
        c.relations["symmetric"] = []

    def test_single_thread_global_variable_if_statement(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], "\
                         "resources=[r1], operations=[o0,1, o0,2, o0,3, o0,4, o1,1, o1,2, o1,3, o1,4], " \
                         "mutexes=[(m, PMN)], edges=[(o0,1, o0,2), (o0,2, o0,3), (o0,3, o0,4), (r1, o1,1), " \
                         "(o1,1, o1,2), (o1,2, o1,4), (o1,2, o1,3), (o1,3, r1), (o1,3, o1,4)], " \
                         "relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "single_thread_global_variable_if_statement.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_single_thread_global_variable_if_else_statement(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], " \
                         "resources=[r1], operations=[o0,1, o0,2, o0,3, o0,4, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6], " \
                         "mutexes=[(m, PMN)], edges=[(o0,1, o0,2), (o0,2, o0,3), (o0,3, o0,4), (r1, o1,1), " \
                         "(o1,1, o1,2), (o1,2, o1,4), (o1,2, o1,3), (o1,3, r1), (o1,3, o1,6), (o1,4, o1,5), " \
                         "(o1,5, r1), (o1,5, o1,6)], relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "single_thread_global_variable_if_else_statement.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_single_thread_global_variable_while_loop(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], "\
                         "resources=[r1], operations=[o0,1, o0,2, o0,3, o0,4, o1,1, o1,2, o1,3, o1,4], " \
                         "mutexes=[(m, PMN)], edges=[(o0,1, o0,2), (o0,2, o0,3), (o0,3, o0,4), (o1,1, o1,4), " \
                         "(o1,1, o1,2), (r1, o1,2), (o1,2, o1,3), (o1,3, o1,1), (o1,3, r1), (o1,3, o1,4)], " \
                         "relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "single_thread_global_variable_while_loop.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_two_threads_global_variable(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1, t2], time_units=[[t0], [t1, t2], " \
                         "[t0]], resources=[r1], operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o0,7, o1,1, o1,2, " \
                         "o1,3, o1,4, o2,1, o2,2, o2,3, o2,4], mutexes=[(m, PMN)], edges=[(o0,1, o0,2), " \
                         "(o0,2, o0,3), (o0,3, o0,4), (o0,4, o0,5), (o0,5, o0,6), (o0,6, o0,7), (q1, o1,1), " \
                         "(o1,1, o1,2), (o1,2, r1), (o1,2, o1,3), (o1,3, q1), (o1,3, o1,4), (q1, o2,1), " \
                         "(o2,1, o2,2), (o2,2, r1), (o2,2, o2,3), (o2,3, q1), (o2,3, o2,4)], " \
                         "relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "two_threads_global_variable.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_single_thread_do_while_loop(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], "\
                         "resources=[r1], operations=[o0,1, o0,2, o0,3, o0,4, o1,1, o1,2, o1,3, o1,4, o1,5, " \
                         "o1,6], mutexes=[(m, PMN)], edges=[(o0,1, o0,2), (o0,2, o0,3), (o0,3, o0,4), (q1, o1,1), " \
                         "(o1,1, o1,2), (o1,2, o1,3), (o1,3, r1), (o1,3, o1,4), (o1,4, o1,2), (o1,4, r1), "\
                         "(o1,4, o1,5), (o1,5, q1), (o1,5, o1,6)], relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "single_thread_do_while_loop.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_single_thread_operation_in_main_thread_for_loop_without_body(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t0, t1], [t0]],"\
                         " resources=[r1], operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o1,1, o1,2, o1,3, o1,4, " \
                         "o1,5, o1,6], mutexes=[(m, PMN)], edges=[(o0,1, o0,2), (o0,2, o0,3), (r1, o0,3), " \
                         "(o0,3, o0,4), (o0,4, o0,5), (q1, o1,1), (o1,1, o1,2), (o1,2, o1,5), (o1,2, o1,3), " \
                         "(r1, o1,3), (o1,3, o1,4), (o1,4, o1,2), (o1,4, r1), (o1,4, o1,5), (o1,5, q1), " \
                         "(o1,5, o1,6)], relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "single_thread_operation_in_main_thread_for_loop_without_body.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_single_thread_for_loop(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], "\
                         "resources=[r1, r2], operations=[o0,1, o0,2, o0,3, o0,4, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6, "\
                         "o1,7, o1,8, o1,9, o1,10, o1,11, o1,12, o1,13], mutexes=[(m, PMN)], edges=[(o0,1, o0,2), " \
                         "(o0,2, o0,3), (o0,3, o0,4), (o1,1, o1,2), (o1,2, o1,3), (o1,3, o1,4), (o1,4, o1,13), " \
                         "(o1,4, o1,5), (r1, o1,5), (r2, o1,5), (o1,5, o1,6), (r1, o1,6), (o1,6, o1,7), (o1,7, o1,8), "\
                         "(o1,8, o1,9), (q1, o1,9), (o1,9, o1,10), (o1,10, r2), (o1,10, o1,11), (o1,11, q1), " \
                         "(o1,11, o1,12), (o1,12, o1,4), (o1,12, o1,13)], relations=(forward=[], backward=[], " \
                         "symmetric=[]))"
        file_to_parse = "single_thread_for_loop.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))
            self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_multiple_file_application(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], " \
                         "resources=[r1, r2], operations=[o0,1, o0,2, o0,3, o0,4, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6, "\
                         "o1,7, o1,8, o1,9, o1,10, o1,11, o1,12, o1,13], mutexes=[(m, PMN)], edges=[(o0,1, o0,2), " \
                         "(o0,2, o0,3), (o0,3, o0,4), (o1,1, o1,2), (o1,2, o1,3), (o1,3, o1,4), (o1,4, o1,13), " \
                         "(o1,4, o1,5), (r1, o1,5), (r2, o1,5), (o1,5, o1,6), (r1, o1,6), (o1,6, o1,7), (o1,7, o1,8), "\
                         "(o1,8, o1,9), (q1, o1,9), (o1,9, o1,10), (o1,10, r2), (o1,10, o1,11), (o1,11, q1), " \
                         "(o1,11, o1,12), (o1,12, o1,4), (o1,12, o1,13)], " \
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
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1, t2], time_units=[[t0], [t1, t2], " \
                         "[t0]], resources=[r1], operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o0,7, o1,1, o1,2, " \
                         "o1,3, o1,4, o2,1, o2,2, o2,3, o2,4], mutexes=[(m, PMN)], edges=[(o0,1, o0,2), (o0,2, o0,3), "\
                         "(o0,3, o0,4), (o0,4, o0,5), (o0,5, o0,6), (o0,6, o0,7), (q1, o1,1), (o1,1, o1,2), " \
                         "(o1,2, r1), (o1,2, o1,3), (o1,3, q1), (o1,3, o1,4), (q1, o2,1), (o2,1, o2,2), (o2,2, r1), " \
                         "(o2,2, o2,3), (o2,3, q1), (o2,3, o2,4)], relations=(forward=[], backward=[], symmetric=[]))"
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
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], " \
                         "resources=[r1], operations=[o0,1, o0,2, o0,3, o0,4, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6], " \
                         "mutexes=[(m, PMN)], edges=[(o0,1, o0,2), (o0,2, o0,3), (o0,3, o0,4), (q1, o1,1), " \
                         "(o1,1, o1,2), (o1,2, o1,3), (o1,3, r1), (o1,3, o1,4), (o1,4, o1,2), (o1,4, r1), " \
                         "(o1,4, o1,5), (o1,5, q1), (o1,5, o1,6)], relations=(forward=[], backward=[], symmetric=[]))"
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
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1, t2], time_units=[[t0], [t1], " \
                         "[t2], [t1], [t0]], resources=[], operations=[o0,1, o0,2, o0,3, o0,4, o1,1, o1,2, o1,3, " \
                         "o1,4, o1,5, o1,6, o2,1, o2,2, o2,3, o2,4], mutexes=[], edges=[(o0,1, o0,2), (o0,2, o0,3), " \
                         "(o0,3, o0,4), (o1,1, o1,2), (o1,2, o1,3), (o1,3, o1,4), (o1,4, o1,5), (o1,5, o1,6), " \
                         "(o2,1, o2,2), (o2,2, o2,3), (o2,3, o2,4)], relations=(forward=[], backward=[], symmetric=[]))"
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
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1, t2], time_units=[[t0], [t1], " \
                         "[t1, t2], [t1], [t0]], resources=[], operations=[o0,1, o0,2, o0,3, o0,4, o1,1, o1,2, o1,3, "\
                         "o1,4, o1,5, o1,6, o1,7, o2,1, o2,2, o2,3, o2,4], mutexes=[], edges=[(o0,1, o0,2), " \
                         "(o0,2, o0,3), (o0,3, o0,4), (o1,1, o1,2), (o1,2, o1,3), (o1,3, o1,4), (o1,4, o1,5), " \
                         "(o1,5, o1,6), (o1,6, o1,7), (o2,1, o2,2), (o2,2, o2,3), (o2,3, o2,4)], " \
                         "relations=(forward=[], backward=[], symmetric=[]))"
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
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1, t2, t3, t4], time_units=[[t0], " \
                         "[t1], [t2], [t3], [t4], [t3], [t2], [t1], [t0]], resources=[], operations=[o0,1, o0,2, " \
                         "o0,3, o0,4, o1,1, o1,2, o1,3, o1,4, o2,1, o2,2, o2,3, o2,4, o3,1, o3,2, o3,3, o3,4, o4,1], " \
                         "mutexes=[], edges=[(o0,1, o0,2), (o0,2, o0,3), (o0,3, o0,4), (o1,1, o1,2), (o1,2, o1,3), " \
                         "(o1,3, o1,4), (o2,1, o2,2), (o2,2, o2,3), (o2,3, o2,4), (o3,1, o3,2), (o3,2, o3,3), " \
                         "(o3,3, o3,4)], relations=(forward=[], backward=[], symmetric=[]))"
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
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1, t2, t3, t4, t5], time_units=[[t0], "\
                         "[t1], [t2, t3], [t4, t5], [t2, t3], [t1], [t0]], resources=[], operations=[o0,1, o0,2, o0,3,"\
                         " o0,4, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6, o1,7, o2,1, o2,2, o2,3, o2,4, o3,1, o3,2, o3,3, " \
                         "o3,4, o4,1, o5,1], mutexes=[], edges=[(o0,1, o0,2), (o0,2, o0,3), (o0,3, o0,4), " \
                         "(o1,1, o1,2), (o1,2, o1,3), (o1,3, o1,4), (o1,4, o1,5), (o1,5, o1,6), (o1,6, o1,7), " \
                         "(o2,1, o2,2), (o2,2, o2,3), (o2,3, o2,4), (o3,1, o3,2), (o3,2, o3,3), (o3,3, o3,4)], " \
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
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], " \
                         "resources=[r1], operations=[o0,1, o0,2, o0,3, o0,4, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6, " \
                         "o1,7, o1,8, o1,9, o1,10, o1,11, o1,12, o1,13, o1,14], mutexes=[], edges=[(o0,1, o0,2), " \
                         "(o0,2, o0,3), (o0,3, o0,4), (o1,1, o1,2), (o1,2, o1,3), (o1,3, o1,4), (o1,4, o1,5), " \
                         "(o1,5, r1), (o1,5, o1,6), (o1,6, r1), (o1,6, o1,7), (o1,7, r1), (o1,7, o1,8), (o1,8, o1,9), "\
                         "(o1,9, o1,13), (o1,9, o1,10), (o1,10, o1,11), (r1, o1,11), (o1,11, o1,12), (o1,12, o1,9), " \
                         "(o1,12, o1,13), (o1,13, r1), (o1,13, o1,14)], " \
                         "relations=(forward=[(o1,5, o1,13)], backward=[], symmetric=[]))"
        file_to_parse = "forward_relation.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_two_forward_relations(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], "\
                         "resources=[r1, r2], operations=[o0,1, o0,2, o0,3, o0,4, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6, "\
                         "o1,7, o1,8, o1,9, o1,10, o1,11, o1,12, o1,13, o1,14, o1,15, o1,16, o1,17, o1,18, o1,19, " \
                         "o1,20, o1,21, o1,22, o1,23, o1,24, o1,25, o1,26, o1,27, o1,28, o1,29, o1,30], " \
                         "mutexes=[], edges=[(o0,1, o0,2), (o0,2, o0,3), (o0,3, o0,4), (o1,1, o1,2), (o1,2, o1,3), " \
                         "(o1,3, o1,4), (o1,4, o1,5), (o1,5, o1,6), (o1,6, o1,7), (o1,7, o1,8), (o1,8, r1), " \
                         "(o1,8, o1,9), (o1,9, o1,10), (o1,10, r2), (o1,10, o1,11), (o1,11, r1), (o1,11, o1,12), " \
                         "(o1,12, r2), (o1,12, o1,13), (o1,13, o1,14), (o1,14, r1), (o1,14, o1,15), (o1,15, o1,16), " \
                         "(o1,16, r2), (o1,16, o1,17), (o1,17, o1,18), (o1,18, o1,22), (o1,18, o1,19), " \
                         "(o1,19, o1,20), (r1, o1,20), (o1,20, o1,21), (o1,21, o1,18), (o1,21, o1,22), " \
                         "(o1,22, o1,23), (o1,23, o1,24), (o1,24, o1,28), (o1,24, o1,25), (o1,25, o1,26), " \
                         "(r2, o1,26), (o1,26, o1,27), (o1,27, o1,24), (o1,27, o1,28), (o1,28, r1), (o1,28, o1,29), " \
                         "(o1,29, r2), (o1,29, o1,30)], relations=(forward=[(o1,8, o1,28), (o1,10, o1,29)], " \
                         "backward=[], symmetric=[]))"
        file_to_parse = "two_forward_relation.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_backward_relation(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], " \
                         "resources=[r1], operations=[o0,1, o0,2, o0,3, o0,4, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6, " \
                         "o1,7, o1,8, o1,9, o1,10, o1,11], mutexes=[], edges=[(o0,1, o0,2), (o0,2, o0,3), " \
                         "(o0,3, o0,4), (o1,1, o1,2), (o1,2, o1,3), (o1,3, r1), (o1,3, o1,4), (o1,4, o1,9), " \
                         "(o1,4, o1,5), (o1,5, o1,6), (o1,6, o1,7), (o1,7, o1,8), (o1,9, o1,10), (o1,10, r1), " \
                         "(o1,10, o1,11)], relations=(forward=[], backward=[(o1,2, o1,5)], symmetric=[]))"
        file_to_parse = "backward_relation.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_two_backward_relations(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], "\
                         "resources=[r1], operations=[o0,1, o0,2, o0,3, o0,4, o1,1, o1,2, o1,3, o1,4, o1,5, " \
                         "o1,6, o1,7, o1,8, o1,9, o1,10, o1,11, o1,12, o1,13, o1,14, o1,15, o1,16, o1,17], " \
                         "mutexes=[], edges=[(o0,1, o0,2), (o0,2, o0,3), (o0,3, o0,4), (o1,1, o1,2), (o1,2, o1,3), " \
                         "(o1,3, o1,4), (o1,4, o1,5), (o1,5, o1,6), (o1,6, o1,7), (o1,7, o1,8), (o1,8, r1), " \
                         "(o1,8, o1,9), (o1,9, o1,14), (o1,9, o1,10), (o1,10, o1,11), (o1,11, o1,12), (o1,12, o1,13), "\
                         "(o1,14, o1,15), (o1,15, r1), (o1,15, o1,16), (o1,16, o1,17)], relations=(forward=[], " \
                         "backward=[(o1,3, o1,4), (o1,7, o1,10)], symmetric=[]))"
        file_to_parse = "two_backward_relation.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_symmetric_relations(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], " \
                         "resources=[], operations=[o0,1, o0,2, o0,3, o0,4, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6, o1,7, " \
                         "o1,8, o1,9, o1,10, o1,11, o1,12, o1,13, o1,14, o1,15, o1,16], mutexes=[], edges=[" \
                         "(o0,1, o0,2), (o0,2, o0,3), (o0,3, o0,4), (o1,1, o1,2), (o1,2, o1,3), (o1,3, o1,4), " \
                         "(o1,4, o1,5), (o1,5, o1,6), (o1,6, o1,12), (o1,6, o1,7), (o1,7, o1,8), (o1,8, o1,9), " \
                         "(o1,9, o1,10), (o1,10, o1,11), (o1,11, o1,6), (o1,11, o1,12), (o1,12, o1,13), " \
                         "(o1,13, o1,14), (o1,14, o1,15), (o1,15, o1,16)], relations=(forward=[], backward=[], " \
                         "symmetric=[(o1,4, o1,8), (o1,8, o1,12)]))"
        file_to_parse = "symmetric_relation.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_symmetric_relations2(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1, t2], time_units=[[t0], [t1, t2], " \
                         "[t0]], resources=[r1, r2], operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o0,7, o0,8, "\
                         "o0,9, o0,10, o0,11, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6, o1,7, o1,8, o1,9, o1,10, o1,11, " \
                         "o1,12, o1,13, o1,14, o2,1, o2,2, o2,3], mutexes=[(m, PMN)], edges=[(o0,1, o0,2), " \
                         "(o0,2, o0,3), (r1, o0,3), (o0,3, o0,4), (r2, o0,4), (o0,4, o0,5), (o0,5, o0,6), " \
                         "(o0,6, o0,7), (o0,7, o0,8), (o0,8, o0,9), (r1, o0,9), (o0,9, o0,10), (r2, o0,10), " \
                         "(o0,10, o0,11), (o1,1, o1,2), (o1,2, o1,14), (o1,2, o1,3), (o1,3, o1,4), (q1, o1,4), " \
                         "(o1,4, o1,5), (o1,5, r1), (o1,5, o1,6), (o1,6, r2), (o1,6, o1,7), (o1,7, q1), " \
                         "(o1,7, o1,8), (o1,8, o1,9), (q1, o1,9), (o1,9, o1,10), (r1, o1,10), (o1,10, o1,11), " \
                         "(r2, o1,11), (o1,11, o1,12), (o1,12, q1), (o1,12, o1,13), (o1,13, o1,2), (o1,13, o1,14), " \
                         "(r1, o2,1), (o2,1, o2,2), (r2, o2,2), (o2,2, o2,3)], " \
                         "relations=(forward=[], backward=[], symmetric=[(o1,5, o1,10), (o1,6, o1,11)]))"
        file_to_parse = "atomicity_violation4.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        c.relations["symmetric"].append(('++', 'printf'))
        c.relations["symmetric"].append(('--', 'printf'))
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_four_threads_in_time_unit(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1, t2, t3, t4], time_units=[[t0], " \
                         "[t1, t2, t3, t4], [t0]], resources=[r1], operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, " \
                         "o0,7, o0,8, o0,9, o0,10, o0,11, o0,12, o0,13, o0,14, o0,15, o1,1, o1,2, o1,3, o1,4, o1,5, " \
                         "o1,6, o2,1, o2,2, o2,3, o2,4, o2,5, o2,6, o3,1, o3,2, o3,3, o3,4, o3,5, o3,6, o4,1, o4,2, " \
                         "o4,3, o4,4, o4,5, o4,6], mutexes=[], edges=[(o0,1, o0,2), (o0,2, o0,3), (o0,3, o0,4), " \
                         "(o0,4, o0,5), (r1, o0,5), (o0,5, o0,6), (o0,6, o0,7), (o0,7, o0,8), (o0,8, o0,9), " \
                         "(o0,9, o0,10), (o0,10, o0,11), (o0,11, o0,12), (o0,12, o0,13), (o0,13, o0,14), (r1, o0,14), "\
                         "(o0,14, o0,15), (o1,1, o1,2), (o1,2, o1,6), (o1,2, o1,3), (o1,3, o1,4), (o1,4, r1), " \
                         "(o1,4, o1,5), (o1,5, o1,2), (o1,5, o1,6), (o2,1, o2,2), (o2,2, o2,6), (o2,2, o2,3), " \
                         "(o2,3, o2,4), (o2,4, r1), (o2,4, o2,5), (o2,5, o2,2), (o2,5, o2,6), (o3,1, o3,2), " \
                         "(o3,2, o3,6), (o3,2, o3,3), (o3,3, o3,4), (o3,4, r1), (o3,4, o3,5), (o3,5, o3,2), " \
                         "(o3,5, o3,6), (o4,1, o4,2), (o4,2, o4,6), (o4,2, o4,3), (o4,3, o4,4), (o4,4, r1), " \
                         "(o4,4, o4,5), (o4,5, o4,2), (o4,5, o4,6)], relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "race_condition4.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_loop_thread_creation(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1, t2], time_units=[[t0], [t0, t1, " \
                         "t2], [t0]], resources=[r1], operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o0,7, o0,8, " \
                         "o0,9, o0,10, o0,11, o0,12, o0,13, o0,14, o0,15, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6, o1,7, " \
                         "o1,8, o2,1, o2,2, o2,3, o2,4, o2,5, o2,6, o2,7, o2,8], mutexes=[], edges=[(o0,1, o0,2), " \
                         "(o0,2, o0,3), (r1, o0,3), (o0,3, o0,4), (o0,4, o0,5), (o0,5, o0,9), (o0,5, o0,6), " \
                         "(o0,6, o0,7), (o0,7, o0,8), (o0,8, o0,5), (o0,8, o0,9), (o0,9, o0,10), (o0,10, o0,14), " \
                         "(o0,10, o0,11), (o0,11, o0,12), (o0,12, o0,13), (o0,13, o0,10), (o0,13, o0,14), " \
                         "(r1, o0,14), (o0,14, o0,15), (r1, o1,1), (o1,1, o1,2), (o1,2, o1,3), (o1,3, o1,7), " \
                         "(o1,3, o1,4), (o1,4, o1,5), (o1,5, r1), (o1,5, o1,6), (o1,6, o1,3), (o1,6, o1,7), " \
                         "(r1, o1,7), (o1,7, o1,8), (r1, o2,1), (o2,1, o2,2), (o2,2, o2,3), (o2,3, o2,7), " \
                         "(o2,3, o2,4), (o2,4, o2,5), (o2,5, r1), (o2,5, o2,6), (o2,6, o2,3), (o2,6, o2,7), " \
                         "(r1, o2,7), (o2,7, o2,8)], relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "race_condition8.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_nested_threads_main_thread_is_parallel(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1, t2, t3], time_units=[[t0], [t1], " \
                         "[t1, t2, t3], [t1], [t0]], resources=[r1], operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, " \
                         "o1,1, o1,2, o1,3, o1,4, o1,5, o1,6, o1,7, o1,8, o1,9, o1,10, o1,11, o1,12, o1,13, o1,14, " \
                         "o1,15, o2,1, o2,2, o2,3, o2,4, o2,5, o2,6, o3,1, o3,2, o3,3, o3,4, o3,5, o3,6], mutexes=[], "\
                         "edges=[(o0,1, o0,2), (r1, o0,2), (o0,2, o0,3), (o0,3, o0,4), (o0,4, o0,5), (r1, o0,5), " \
                         "(o0,5, o0,6), (o1,1, o1,2), (o1,2, o1,3), (o1,3, o1,4), (o1,4, o1,8), (o1,4, o1,5), " \
                         "(o1,5, o1,6), (o1,6, o1,7), (o1,7, o1,4), (o1,7, o1,8), (r1, o1,8), (o1,8, o1,9), " \
                         "(o1,9, o1,10), (o1,10, o1,14), (o1,10, o1,11), (o1,11, o1,12), (o1,12, o1,13), " \
                         "(o1,13, o1,10), (o1,13, o1,14), (r1, o1,14), (o1,14, o1,15), (o2,1, o2,2), (o2,2, o2,6), " \
                         "(o2,2, o2,3), (o2,3, o2,4), (o2,4, r1), (o2,4, o2,5), (o2,5, o2,2), (o2,5, o2,6), " \
                         "(o3,1, o3,2), (o3,2, o3,6), (o3,2, o3,3), (o3,3, o3,4), (o3,4, r1), (o3,4, o3,5), " \
                         "(o3,5, o3,2), (o3,5, o3,6)], relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "race_condition10.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        main_thread, *other_threads = result.threads
        self.assertEqual(0, main_thread.depth, "Main thread does not have expected depth!")
        for thread, depth in zip(other_threads, [1, 2, 2]):
            self.assertEqual(depth, thread.depth, "Nested thread does not have expected depth!")
        self.assertEqual(expected_mascm, str(result))

    def test_ignoring_nested_threads(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1, t2, t3], time_units=[[t0], " \
                         "[t0, t1], [t0, t1, t2, t3], [t0, t1], [t0]], resources=[r1], operations=[o0,1, o0,2, o0,3, "\
                         "o0,4, o0,5, o0,6, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6, o1,7, o1,8, o1,9, o1,10, o1,11, " \
                         "o1,12, o1,13, o1,14, o1,15, o2,1, o2,2, o2,3, o2,4, o2,5, o2,6, o3,1, o3,2, o3,3, o3,4, " \
                         "o3,5, o3,6], mutexes=[], edges=[(o0,1, o0,2), (o0,2, o0,3), (r1, o0,3), (o0,3, o0,4), " \
                         "(o0,4, o0,5), (r1, o0,5), (o0,5, o0,6), (o1,1, o1,2), (o1,2, o1,3), (r1, o1,3), " \
                         "(o1,3, o1,4), (o1,4, o1,5), (o1,5, o1,9), (o1,5, o1,6), (o1,6, o1,7), (o1,7, o1,8), " \
                         "(o1,8, o1,5), (o1,8, o1,9), (o1,9, o1,10), (o1,10, o1,14), (o1,10, o1,11), (o1,11, o1,12), "\
                         "(o1,12, o1,13), (o1,13, o1,10), (o1,13, o1,14), (r1, o1,14), (o1,14, o1,15), (o2,1, o2,2), " \
                         "(o2,2, o2,6), (o2,2, o2,3), (o2,3, o2,4), (o2,4, r1), (o2,4, o2,5), (o2,5, o2,2), " \
                         "(o2,5, o2,6), (o3,1, o3,2), (o3,2, o3,6), (o3,2, o3,3), (o3,3, o3,4), (o3,4, r1), " \
                         "(o3,4, o3,5), (o3,5, o3,2), (o3,5, o3,6)], relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "race_condition11.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        main_thread, *other_threads = result.threads
        self.assertEqual(0, main_thread.depth, "Main thread does not have expected depth!")
        for thread, depth in zip(other_threads, [1, 2, 2]):
            self.assertEqual(depth, thread.depth, "Nested thread does not have expected depth!")
        self.assertEqual(expected_mascm, str(result))

    def test_recursion0(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0], time_units=[[t0]], resources=[r1], " \
                         "operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o0,7, o0,8, o0,9, o0,10, o0,11, o0,12, " \
                         "o0,13, o0,14, o0,15, o0,16], mutexes=[], edges=[(o0,1, o0,2), (o0,2, o0,3), (o0,3, o0,4), " \
                         "(o0,4, o0,5), (o0,5, o0,6), (o0,6, o0,7), (o0,7, o0,9), (o0,7, o0,8), (o0,8, o0,13), " \
                         "(o0,9, o0,10), (o0,10, o0,11), (o0,11, o0,12), (o0,12, o0,13), (o0,13, o0,12), " \
                         "(o0,13, o0,14), (o0,14, r1), (o0,14, o0,15), (r1, o0,15), (o0,15, o0,16)], " \
                         "relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "recursion0.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_recursion0a(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0], time_units=[[t0]], resources=[r1], " \
                         "operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o0,7, o0,8, o0,9, o0,10, o0,11, o0,12, " \
                         "o0,13], mutexes=[], edges=[(o0,1, o0,2), (o0,2, o0,3), (o0,3, o0,4), (o0,4, o0,5), " \
                         "(o0,5, o0,7), (o0,5, o0,6), (o0,6, o0,4), (o0,6, o0,11), (o0,7, o0,8), (o0,8, o0,9), " \
                         "(o0,9, o0,10), (o0,10, o0,4), (o0,10, o0,11), (o0,11, r1), (o0,11, o0,12), (r1, o0,12), " \
                         "(o0,12, o0,13)], relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "recursion0a.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_recursion1(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], " \
                         "resources=[r1, r2], operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o0,7, o0,8, o1,1, o1,2, "\
                         "o1,3, o1,4, o1,5, o1,6, o1,7, o1,8, o1,9, o1,10], mutexes=[], edges=[(o0,1, o0,2), " \
                         "(o0,2, o0,3), (o0,3, o0,4), (o0,4, o0,5), (o0,5, o0,6), (o0,6, o0,7), (r1, o0,7), " \
                         "(o0,7, o0,8), (o1,1, o1,2), (o1,2, o1,3), (o1,3, o1,7), (o1,3, o1,4), (o1,4, o1,5), " \
                         "(r2, o1,5), (o1,5, o1,6), (o1,6, o1,2), (o1,6, o1,9), (o1,7, o1,8), (o1,8, o1,2), " \
                         "(o1,8, o1,9), (o1,9, r1), (o1,9, o1,10)], relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "recursion1.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_recursion2(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], " \
                         "resources=[r1, r2], operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o0,7, o0,8, o1,1, o1,2, "\
                         "o1,3, o1,4, o1,5, o1,6, o1,7, o1,8, o1,9, o1,10, o1,11, o1,12, o1,13], mutexes=[], edges=[" \
                         "(o0,1, o0,2), (o0,2, o0,3), (o0,3, o0,4), (o0,4, o0,5), (o0,5, o0,6), (o0,6, o0,7), " \
                         "(r1, o0,7), (o0,7, o0,8), (o1,1, o1,2), (o1,2, o1,3), (r2, o1,3), (o1,3, o1,4), " \
                         "(o1,4, o1,5), (o1,5, o1,7), (o1,5, o1,6), (o1,6, o1,11), (o1,7, o1,8), (o1,8, o1,9), " \
                         "(r2, o1,9), (o1,9, o1,10), (o1,10, o1,11), (o1,11, o1,10), (o1,11, o1,12), (o1,12, r1), " \
                         "(o1,12, o1,13)], relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "recursion2.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_recursion3(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], " \
                         "resources=[r1, r2], operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o0,7, o0,8, o0,9, " \
                         "o0,10, o0,11, o0,12, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6, o1,7, o1,8, o1,9, o1,10, o1,11, " \
                         "o1,12], mutexes=[(m, PMR)], edges=[(o0,1, o0,2), (o0,2, o0,3), (o0,3, o0,4), (o0,4, o0,5), " \
                         "(o0,5, o0,6), (o0,6, o0,7), (o0,7, o0,8), (o0,8, o0,9), (o0,9, o0,10), (o0,10, o0,11), " \
                         "(r1, o0,11), (o0,11, o0,12), (o1,1, o1,2), (o1,2, o1,3), (q1, o1,3), (o1,3, o1,4), " \
                         "(o1,4, o1,8), (o1,4, o1,5), (o1,5, o1,6), (r2, o1,6), (o1,6, o1,7), (o1,7, o1,2), " \
                         "(o1,7, o1,10), (o1,8, o1,9), (o1,9, o1,2), (o1,9, o1,11), (o1,10, q1), (o1,10, o1,11), " \
                         "(o1,11, r1), (o1,11, o1,12)], relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "recursion3.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_order_violation1(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1, t2], time_units=[[t0], [t1, t2], " \
                         "[t0]], resources=[r1], operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o0,7, o0,8, o0,9, " \
                         "o0,10, o0,11, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6, o1,7, o1,8, o2,1, o2,2, o2,3, o2,4, o2,5, "\
                         "o2,6, o2,7, o2,8, o2,9, o2,10], mutexes=[(m, PMN)], edges=[(o0,1, o0,2), (o0,2, o0,3), " \
                         "(o0,3, o0,4), (o0,4, o0,5), (o0,5, o0,6), (o0,6, o0,7), (o0,7, o0,8), (o0,8, r1), " \
                         "(o0,8, o0,9), (r1, o0,9), (o0,9, o0,10), (o0,10, r1), (o0,10, o0,11), (q1, o1,1), " \
                         "(o1,1, o1,2), (o1,2, o1,3), (o1,3, r1), (o1,3, o1,4), (o1,4, r1), (o1,4, o1,5), (o1,5, r1), "\
                         "(o1,5, o1,6), (r1, o1,6), (o1,6, o1,7), (o1,7, q1), (o1,7, o1,8), (o2,1, o2,2), (q1, o2,2), "\
                         "(o2,2, o2,3), (o2,3, o2,4), (o2,4, o2,9), (o2,4, o2,5), (o2,5, o2,6), (o2,6, r1), " \
                         "(o2,6, o2,7), (o2,7, r1), (o2,7, o2,8), (o2,8, o2,4), (o2,8, o2,9), (o2,9, q1), " \
                         "(o2,9, o2,10)], relations=(forward=[], backward=[(o1,3, o2,7)], symmetric=[]))"
        c.relations["backward"].append(('malloc', '++'))
        file_to_parse = "order_violation1.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_order_violation2(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1, t2, t3], time_units=[[t0], " \
                         "[t1, t2, t3], [t0]], resources=[r1], operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o0,7, " \
                         "o0,8, o0,9, o0,10, o0,11, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6, o1,7, o1,8, o2,1, o2,2, o2,3, "\
                         "o2,4, o2,5, o2,6, o2,7, o2,8, o2,9, o2,10, o3,1, o3,2, o3,3, o3,4, o3,5, o3,6, o3,7, o3,8, " \
                         "o3,9], mutexes=[(m, PMN)], edges=[(o0,1, o0,2), (o0,2, o0,3), (o0,3, o0,4), (o0,4, o0,5), " \
                         "(o0,5, o0,6), (o0,6, o0,7), (o0,7, o0,8), (o0,8, o0,9), (o0,9, o0,10), (o0,10, o0,11), " \
                         "(q1, o1,1), (o1,1, o1,2), (o1,2, o1,3), (o1,3, r1), (o1,3, o1,4), (o1,4, r1), (o1,4, o1,5), "\
                         "(o1,5, r1), (o1,5, o1,6), (r1, o1,6), (o1,6, o1,7), (o1,7, q1), (o1,7, o1,8), (o2,1, o2,2), "\
                         "(q1, o2,2), (o2,2, o2,3), (o2,3, o2,4), (o2,4, o2,9), (o2,4, o2,5), (o2,5, o2,6), " \
                         "(o2,6, r1), (o2,6, o2,7), (o2,7, r1), (o2,7, o2,8), (o2,8, o2,4), (o2,8, o2,9), (o2,9, q1), "\
                         "(o2,9, o2,10), (q1, o3,1), (o3,1, o3,2), (o3,2, o3,3), (o3,3, r1), (o3,3, o3,4), (o3,4, r1),"\
                         " (o3,4, o3,5), (r1, o3,5), (o3,5, o3,6), (o3,6, r1), (o3,6, o3,7), (o3,7, r1), (o3,7, o3,8),"\
                         " (o3,8, q1), (o3,8, o3,9)], relations=(forward=[(o1,3, o3,7)], backward=[(o1,3, o2,7)], " \
                         "symmetric=[]))"
        c.relations["backward"].append(('malloc', '++'))
        file_to_parse = "order_violation2.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_no_race_condition5_model(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1, t2], time_units=[[t0], [t1], [t2], "\
                         "[t0]], resources=[r1], operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o0,7, o0,8, o0,9, " \
                         "o1,1, o1,2, o1,3, o1,4, o1,5, o1,6, o2,1, o2,2, o2,3, o2,4, o2,5, o2,6], mutexes=[], edges=["\
                         "(o0,1, o0,2), (o0,2, o0,3), (r1, o0,3), (o0,3, o0,4), (o0,4, o0,5), (o0,5, o0,6), " \
                         "(o0,6, o0,7), (o0,7, o0,8), (r1, o0,8), (o0,8, o0,9), (o1,1, o1,2), (o1,2, o1,6), " \
                         "(o1,2, o1,3), (o1,3, o1,4), (o1,4, r1), (o1,4, o1,5), (o1,5, o1,2), (o1,5, o1,6), " \
                         "(o2,1, o2,2), (o2,2, o2,6), (o2,2, o2,3), (o2,3, o2,4), (o2,4, r1), (o2,4, o2,5), " \
                         "(o2,5, o2,2), (o2,5, o2,6)], relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "no_race_condition5.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_no_race_condition6_model(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1, t2, t3, t4], time_units=[[t0], " \
                         "[t1], [t2], [t3], [t4], [t0]], resources=[r1], operations=[o0,1, o0,2, o0,3, o0,4, o0,5, " \
                         "o0,6, o0,7, o0,8, o0,9, o0,10, o0,11, o0,12, o0,13, o0,14, o0,15, o1,1, o1,2, o1,3, o1,4, " \
                         "o1,5, o1,6, o2,1, o2,2, o2,3, o2,4, o2,5, o2,6, o3,1, o3,2, o3,3, o3,4, o3,5, o3,6, o4,1, " \
                         "o4,2, o4,3, o4,4, o4,5, o4,6], mutexes=[], edges=[(o0,1, o0,2), (o0,2, o0,3), (o0,3, o0,4), "\
                         "(o0,4, o0,5), (r1, o0,5), (o0,5, o0,6), (o0,6, o0,7), (o0,7, o0,8), (o0,8, o0,9), " \
                         "(o0,9, o0,10), (o0,10, o0,11), (o0,11, o0,12), (o0,12, o0,13), (o0,13, o0,14), (r1, o0,14), "\
                         "(o0,14, o0,15), (o1,1, o1,2), (o1,2, o1,6), (o1,2, o1,3), (o1,3, o1,4), (o1,4, r1), " \
                         "(o1,4, o1,5), (o1,5, o1,2), (o1,5, o1,6), (o2,1, o2,2), (o2,2, o2,6), (o2,2, o2,3), " \
                         "(o2,3, o2,4), (o2,4, r1), (o2,4, o2,5), (o2,5, o2,2), (o2,5, o2,6), (o3,1, o3,2), " \
                         "(o3,2, o3,6), (o3,2, o3,3), (o3,3, o3,4), (o3,4, r1), (o3,4, o3,5), (o3,5, o3,2), " \
                         "(o3,5, o3,6), (o4,1, o4,2), (o4,2, o4,6), (o4,2, o4,3), (o4,3, o4,4), (o4,4, r1), " \
                         "(o4,4, o4,5), (o4,5, o4,2), (o4,5, o4,6)], relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "no_race_condition6.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_no_race_condition7_model(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1, t2, t3, t4, t5], time_units=[[t0], "\
                         "[t1], [t2], [t3], [t4], [t5], [t1], [t0]], resources=[r1], operations=[o0,1, o0,2, o0,3, " \
                         "o0,4, o1,1, o1,2, o1,3, o1,4, o1,5, o1,6, o1,7, o1,8, o1,9, o1,10, o1,11, o1,12, o1,13, " \
                         "o1,14, o1,15, o2,1, o2,2, o2,3, o2,4, o2,5, o2,6, o3,1, o3,2, o3,3, o3,4, o3,5, o3,6, o4,1, "\
                         "o4,2, o4,3, o4,4, o4,5, o4,6, o5,1, o5,2, o5,3, o5,4, o5,5, o5,6], mutexes=[], edges=[" \
                         "(o0,1, o0,2), (o0,2, o0,3), (o0,3, o0,4), (o1,1, o1,2), (o1,2, o1,3), (o1,3, o1,4), " \
                         "(o1,4, o1,5), (r1, o1,5), (o1,5, o1,6), (o1,6, o1,7), (o1,7, o1,8), (o1,8, o1,9), " \
                         "(o1,9, o1,10), (o1,10, o1,11), (o1,11, o1,12), (o1,12, o1,13), (o1,13, o1,14), (r1, o1,14), "\
                         "(o1,14, o1,15), (o2,1, o2,2), (o2,2, o2,6), (o2,2, o2,3), (o2,3, o2,4), (o2,4, r1), " \
                         "(o2,4, o2,5), (o2,5, o2,2), (o2,5, o2,6), (o3,1, o3,2), (o3,2, o3,6), (o3,2, o3,3), " \
                         "(o3,3, o3,4), (o3,4, r1), (o3,4, o3,5), (o3,5, o3,2), (o3,5, o3,6), (o4,1, o4,2), " \
                         "(o4,2, o4,6), (o4,2, o4,3), (o4,3, o4,4), (o4,4, r1), (o4,4, o4,5), (o4,5, o4,2), " \
                         "(o4,5, o4,6), (o5,1, o5,2), (o5,2, o5,6), (o5,2, o5,3), (o5,3, o5,4), (o5,4, r1), " \
                         "(o5,4, o5,5), (o5,5, o5,2), (o5,5, o5,6)], relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "no_race_condition7.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        main_thread, *other_threads = result.threads
        self.assertEqual(0, main_thread.depth, "Main thread does not have expected depth!")
        for thread, depth in zip(other_threads, [1, 2, 2, 2, 2]):
            self.assertEqual(depth, thread.depth, "Nested thread does not have expected depth!")
        self.assertEqual(expected_mascm, str(result))

    def test_deadlock_double1_model(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0, t1], time_units=[[t0], [t1], [t0]], " \
                         "resources=[r1], operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o1,1, o1,2, o1,3, o1,4, " \
                         "o1,5, o1,6, o1,7, o1,8, o1,9, o1,10], mutexes=[(m, PMN)], edges=[(o0,1, o0,2), (r1, o0,2), " \
                         "(o0,2, o0,3), (o0,3, o0,4), (o0,4, o0,5), (r1, o0,5), (o0,5, o0,6), (o1,1, o1,2), " \
                         "(q1, o1,2), (o1,2, o1,3), (q1, o1,3), (o1,3, o1,4), (o1,4, o1,5), (o1,5, r1), " \
                         "(o1,5, o1,6), (o1,6, o1,7), (o1,7, o1,8), (o1,8, o1,4), (o1,8, o1,9), (o1,9, q1), " \
                         "(o1,9, o1,10)], relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "deadlock_double_lock1.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_parse_for_loop_with_break1(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0], time_units=[[t0]], " \
                         "resources=[], operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o0,7, o0,8, o0,9], mutexes=[],"\
                         " edges=[(o0,1, o0,2), (o0,2, o0,9), (o0,2, o0,3), (o0,3, o0,4), (o0,4, o0,6), (o0,4, o0,5), "\
                         "(o0,5, o0,8), (o0,6, o0,7), (o0,7, o0,9), (o0,8, o0,2), (o0,8, o0,9)], " \
                         "relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "for_loop_with_break1.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_parse_for_loop_with_break2(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0], time_units=[[t0]], " \
                         "resources=[], operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o0,7, o0,8, o0,9], mutexes=[],"\
                         " edges=[(o0,1, o0,2), (o0,2, o0,9), (o0,2, o0,3), (o0,3, o0,4), (o0,4, o0,6), (o0,4, o0,5), "\
                         "(o0,5, o0,9), (o0,6, o0,7), (o0,7, o0,8), (o0,8, o0,2), (o0,8, o0,9)], " \
                         "relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "for_loop_with_break2.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_parse_for_loop_with_break3(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0], time_units=[[t0]], " \
                         "resources=[], operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o0,7, o0,8, o0,9], mutexes=[],"\
                         " edges=[(o0,1, o0,2), (o0,2, o0,9), (o0,2, o0,3), (o0,3, o0,4), (o0,4, o0,6), (o0,4, o0,5), "\
                         "(o0,5, o0,8), (o0,6, o0,7), (o0,7, o0,9), (o0,8, o0,2), (o0,8, o0,9)], " \
                         "relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "for_loop_with_break3.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_parse_for_loop_with_break4(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0], time_units=[[t0]], " \
                         "resources=[], operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o0,7, o0,8, o0,9], mutexes=[],"\
                         " edges=[(o0,1, o0,2), (o0,2, o0,9), (o0,2, o0,3), (o0,3, o0,4), (o0,4, o0,6), (o0,4, o0,5), "\
                         "(o0,5, o0,9), (o0,6, o0,7), (o0,7, o0,8), (o0,8, o0,2), (o0,8, o0,9)], " \
                         "relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "for_loop_with_break4.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_parse_while_loop_with_break1(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0], time_units=[[t0]], " \
                         "resources=[], operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o0,7, o0,8, o0,9], mutexes=[],"\
                         " edges=[(o0,1, o0,2), (o0,2, o0,9), (o0,2, o0,3), (o0,3, o0,4), (o0,4, o0,6), (o0,4, o0,5), "\
                         "(o0,5, o0,8), (o0,6, o0,7), (o0,7, o0,9), (o0,8, o0,2), (o0,8, o0,9)], " \
                         "relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "while_loop_with_break1.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_parse_while_loop_with_break2(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0], time_units=[[t0]], " \
                         "resources=[], operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o0,7, o0,8, o0,9], mutexes=[],"\
                         " edges=[(o0,1, o0,2), (o0,2, o0,9), (o0,2, o0,3), (o0,3, o0,4), (o0,4, o0,6), (o0,4, o0,5), "\
                         "(o0,5, o0,9), (o0,6, o0,7), (o0,7, o0,8), (o0,8, o0,2), (o0,8, o0,9)], " \
                         "relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "while_loop_with_break2.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_parse_while_loop_with_break3(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0], time_units=[[t0]], " \
                         "resources=[], operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o0,7, o0,8, o0,9], mutexes=[],"\
                         " edges=[(o0,1, o0,2), (o0,2, o0,9), (o0,2, o0,3), (o0,3, o0,4), (o0,4, o0,5), (o0,5, o0,7), "\
                         "(o0,5, o0,6), (o0,7, o0,8), (o0,8, o0,9)], " \
                         "relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "while_loop_with_break3.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_parse_while_loop_with_break4(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0], time_units=[[t0]], " \
                         "resources=[], operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o0,7, o0,8, o0,9], mutexes=[],"\
                         " edges=[(o0,1, o0,2), (o0,2, o0,9), (o0,2, o0,3), (o0,3, o0,4), (o0,4, o0,5), "\
                         "(o0,5, o0,7), (o0,5, o0,6), (o0,6, o0,9), (o0,7, o0,8), (o0,8, o0,2), (o0,8, o0,9)], " \
                         "relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "while_loop_with_break4.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_parse_do_while_loop_with_break1(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0], time_units=[[t0]], resources=[], " \
                         "operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o0,7, o0,8, o0,9, o0,10], mutexes=[],"\
                         " edges=[(o0,1, o0,2), (o0,2, o0,3), (o0,3, o0,5), (o0,3, o0,4), (o0,4, o0,7), "\
                         "(o0,5, o0,6), (o0,6, o0,10), (o0,7, o0,8), (o0,8, o0,9), (o0,9, o0,2), (o0,9, o0,10)], " \
                         "relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "do_while_loop_with_break1.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_parse_do_while_loop_with_break2(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0], time_units=[[t0]], resources=[], " \
                         "operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o0,7, o0,8, o0,9, o0,10], mutexes=[],"\
                         " edges=[(o0,1, o0,2), (o0,2, o0,3), (o0,3, o0,5), (o0,3, o0,4), (o0,4, o0,10), "\
                         "(o0,5, o0,6), (o0,6, o0,7), (o0,7, o0,8), (o0,8, o0,9), (o0,9, o0,2), (o0,9, o0,10)], " \
                         "relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "do_while_loop_with_break2.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))

    def test_parse_do_while_loop_with_break3(self):
        expected_mascm = "MultithreadedApplicationSourceCodeModel(threads=[t0], time_units=[[t0]], resources=[], " \
                         "operations=[o0,1, o0,2, o0,3, o0,4, o0,5, o0,6, o0,7, o0,8, o0,9, o0,10], mutexes=[],"\
                         " edges=[(o0,1, o0,2), (o0,2, o0,3), (o0,3, o0,5), (o0,3, o0,4), (o0,4, o0,7), "\
                         "(o0,5, o0,6), (o0,6, o0,10), (o0,7, o0,8), (o0,8, o0,9), (o0,9, o0,2), (o0,9, o0,10)], " \
                         "relations=(forward=[], backward=[], symmetric=[]))"
        file_to_parse = "do_while_loop_with_break3.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            result = create_mascm(deque([ast]))

        self.__test_thread_nesting(result.threads)
        self.assertEqual(expected_mascm, str(result))


if "__main__" == __name__:
    unittest.main()
