#!/usr/bin/env python3.7

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.2"

from collections import deque
from helpers.purifier import purify
from mascm import create_mascm
from os.path import join
from pycparser import parse_file
from rdao.race_condition import detect_race_condition
from tests.test_base import TestBase
import unittest


class DetectRaceConditionTest(unittest.TestCase, TestBase):
    def test_race_condition1(self):
        file_to_parse = "race_condition1.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertEqual(2, len(result), "Unexpected edges in the result.")
        self.assertEqual(result[0], mascm.edges[7])
        self.assertEqual(result[1], mascm.edges[12])

    def test_race_condition2(self):
        file_to_parse = "race_condition2.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertEqual(1, len(result), "Unexpected edges in the result.")
        self.assertEqual(result[0], mascm.edges[16])

    def test_race_condition3(self):
        file_to_parse = "race_condition3.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertEqual(2, len(result), "Unexpected edges in the result.")
        self.assertEqual(result[0], mascm.edges[9])
        self.assertEqual(result[1], mascm.edges[18])

    def test_race_condition4(self):
        file_to_parse = "race_condition4.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertEqual(4, len(result), "Unexpected edges in the result.")
        self.assertEqual(result[0], mascm.edges[9])
        self.assertEqual(result[1], mascm.edges[14])
        self.assertEqual(result[2], mascm.edges[19])
        self.assertEqual(result[3], mascm.edges[24])

    def test_race_condition5(self):
        file_to_parse = "race_condition5.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertEqual(1, len(result), "Unexpected edges in the result.")
        self.assertEqual(result[0], mascm.edges[13])

    def test_race_condition6(self):
        file_to_parse = "race_condition6.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertEqual(1, len(result), "Unexpected edges in the result.")
        self.assertEqual(result[0], mascm.edges[13])

    def test_race_condition7(self):
        file_to_parse = "race_condition7.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertEqual(1, len(result), "Unexpected edges in the result.")
        self.assertEqual(result[0], mascm.edges[19])

    def test_race_condition8(self):
        file_to_parse = "race_condition8.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertEqual(6, len(result), "Unexpected edges in the result.")
        self.assertEqual(result[0], mascm.edges[12])
        self.assertEqual(result[1], mascm.edges[15])
        self.assertEqual(result[2], mascm.edges[19])
        self.assertEqual(result[3], mascm.edges[21])
        self.assertEqual(result[4], mascm.edges[24])
        self.assertEqual(result[5], mascm.edges[28])

    def test_no_race_condition1(self):
        file_to_parse = "no_race_condition1.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertListEqual(result, [])

    def test_no_race_condition2(self):
        file_to_parse = "no_race_condition2.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertListEqual(result, [])

    def test_no_race_condition3(self):
        file_to_parse = "no_race_condition3.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertListEqual(result, [])

    def test_no_race_condition4(self):
        file_to_parse = "no_race_condition4.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertListEqual(result, [])

    def test_no_race_condition5(self):
        file_to_parse = "no_race_condition5.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertListEqual(result, [])

    def test_no_race_condition6(self):
        file_to_parse = "no_race_condition6.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_race_condition(mascm))
        self.assertListEqual(result, [])


if "__main__" == __name__:
    unittest.main()
