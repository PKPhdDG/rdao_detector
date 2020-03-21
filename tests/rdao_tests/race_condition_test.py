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
        self.assertEqual(result[0], mascm.edges[7])
        self.assertEqual(result[1], mascm.edges[12])


if "__main__" == __name__:
    unittest.main()
