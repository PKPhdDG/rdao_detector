#!/usr/bin/env python3.8

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "1.1"

from collections import deque
from helpers.purifier import purify
from mascm import create_mascm
from os.path import join
from pycparser import parse_file
from rdao import detect_race_condition
from tests.test_base import TestBase
import unittest

# TODO check cases with structures


class DetectRaceConditionTest(unittest.TestCase, TestBase):
    def test_race_condition1(self):
        file_to_parse = "race_condition1.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertEqual(2, len(result), "Unexpected edges in the result.")
        self.assertEqual(mascm.edges[14], result[0])
        self.assertEqual(mascm.edges[22], result[1])

    def test_race_condition2(self):
        file_to_parse = "race_condition2.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertEqual(1, len(result), "Unexpected edges in the result.")
        self.assertEqual(mascm.edges[26], result[0])

    def test_race_condition3(self):
        file_to_parse = "race_condition3.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertEqual(2, len(result), "Unexpected edges in the result.")
        self.assertEqual(mascm.edges[16], result[0])
        self.assertEqual(mascm.edges[28], result[1])

    def test_race_condition4(self):
        file_to_parse = "race_condition4.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertEqual(4, len(result), "Unexpected edges in the result.")
        self.assertEqual(mascm.edges[20], result[0])
        self.assertEqual(mascm.edges[28], result[1])
        self.assertEqual(mascm.edges[36], result[2])
        self.assertEqual(mascm.edges[44], result[3])

    def test_race_condition5(self):
        file_to_parse = "race_condition5.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertEqual(1, len(result), "Unexpected edges in the result.")
        self.assertEqual(mascm.edges[20], result[0])

    def test_race_condition6(self):
        file_to_parse = "race_condition6.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertEqual(1, len(result), "Unexpected edges in the result.")
        self.assertEqual(mascm.edges[20], result[0])

    def test_race_condition7(self):
        file_to_parse = "race_condition7.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertEqual(1, len(result), "Unexpected edges in the result.")
        self.assertEqual(mascm.edges[26], result[0])

    def test_race_condition8(self):
        file_to_parse = "race_condition8.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertEqual(6, len(result), "Unexpected edges in the result.")
        self.assertEqual(mascm.edges[20], result[0])
        self.assertEqual(mascm.edges[26], result[1])
        self.assertEqual(mascm.edges[30], result[2])
        self.assertEqual(mascm.edges[32], result[3])
        self.assertEqual(mascm.edges[38], result[4])
        self.assertEqual(mascm.edges[42], result[5])

    def test_race_condition9(self):
        file_to_parse = "race_condition9.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertEqual(2, len(result), "Unexpected edges in the result.")
        self.assertEqual(mascm.edges[31], result[0])
        self.assertEqual(mascm.edges[39], result[1])

    def test_race_condition10(self):
        file_to_parse = "race_condition10.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertEqual(3, len(result), "Unexpected edges in the result.")
        self.assertEqual(mascm.edges[16], result[0])
        self.assertEqual(mascm.edges[31], result[1])
        self.assertEqual(mascm.edges[39], result[2])

    def test_race_condition11(self):
        file_to_parse = "race_condition11.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertEqual(5, len(result), "Unexpected edges in the result.")
        self.assertEqual(mascm.edges[2], result[0])
        self.assertEqual(mascm.edges[9], result[1])
        self.assertEqual(mascm.edges[25], result[2])
        self.assertEqual(mascm.edges[31], result[3])
        self.assertEqual(mascm.edges[39], result[4])

    def test_no_race_condition1(self):
        file_to_parse = "no_race_condition1.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertListEqual([], result)

    def test_no_race_condition2(self):
        file_to_parse = "no_race_condition2.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertListEqual([], result)

    def test_no_race_condition3(self):
        file_to_parse = "no_race_condition3.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertListEqual([], result)

    def test_no_race_condition4(self):
        file_to_parse = "no_race_condition4.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertListEqual([], result)

    def test_no_race_condition5(self):
        file_to_parse = "no_race_condition5.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertListEqual([], result)

    def test_no_race_condition6(self):
        file_to_parse = "no_race_condition6.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertListEqual([], result)

    def test_no_race_condition7(self):
        file_to_parse = "deadlock1.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertListEqual([], result)


if "__main__" == __name__:
    unittest.main()
