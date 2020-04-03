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
from rdao import detect_deadlock
from tests.test_base import TestBase
import unittest


class DetectDeadlockTest(unittest.TestCase, TestBase):
    def test_deadlock1(self):
        file_to_parse = "deadlock1.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_deadlock(mascm))
        self.assertEqual(1, len(result), "Unexpected number of results.")
        self.assertEqual(2, len(result[0]), "Unexpected edges in the result.")
        self.assertEqual(mascm.edges[6], result[0][0][0])
        self.assertEqual(mascm.edges[8], result[0][0][1])
        self.assertEqual(mascm.edges[19], result[0][1][0])
        self.assertEqual(mascm.edges[21], result[0][1][1])

    def test_deadlock2(self):
        file_to_parse = "deadlock2.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_deadlock(mascm))
        self.assertEqual(3, len(result), "Unexpected number of results.")
        self.assertEqual(2, len(result[0]), "Unexpected edges in the result.")
        self.assertEqual(2, len(result[1]), "Unexpected edges in the result.")
        self.assertEqual(2, len(result[2]), "Unexpected edges in the result.")
        # First pair
        self.assertEqual(mascm.edges[6], result[0][0][0])
        self.assertEqual(mascm.edges[8], result[0][0][1])
        self.assertEqual(mascm.edges[25], result[0][1][0])
        self.assertEqual(mascm.edges[27], result[0][1][1])

        # Second pair
        self.assertEqual(mascm.edges[6], result[1][0][0])
        self.assertEqual(mascm.edges[10], result[1][0][1])
        self.assertEqual(mascm.edges[23], result[1][1][0])
        self.assertEqual(mascm.edges[27], result[1][1][1])

        # Third pair
        self.assertEqual(mascm.edges[8], result[2][0][0])
        self.assertEqual(mascm.edges[10], result[2][0][1])
        self.assertEqual(mascm.edges[23], result[2][1][0])
        self.assertEqual(mascm.edges[25], result[2][1][1])

    def test_no_deadlock1(self):
        file_to_parse = "no_deadlock1.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_deadlock(mascm))
        self.assertListEqual([], result)


if "__main__" == __name__:
    unittest.main()
