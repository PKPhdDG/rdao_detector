#!/usr/bin/env python3.8

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

import config as c
from collections import deque
from helpers.purifier import purify
from mascm import create_mascm
from os.path import join
from pycparser import parse_file
from rdao import detect_order_violation
from tests.test_base import TestBase
import unittest


class DetectOrderViolationTest(unittest.TestCase, TestBase):
    def tearDown(self) -> None:
        super(DetectOrderViolationTest, self).tearDown()
        c.relations["forward"] = []
        c.relations["backward"] = []
        c.relations["symmetric"] = []

    def test_order_violation1(self):
        file_to_parse = "order_violation1.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        c.relations["backward"].append(('malloc', '++'))
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_order_violation(mascm))

        self.assertEqual(1, len(result))
        self.assertEqual(mascm.operations[13], result[0][0])
        self.assertEqual(mascm.operations[25], result[0][1])
        self.assertEqual(mascm.resources[0], result[0][2])

    def test_order_violation2(self):
        file_to_parse = "order_violation2.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        c.relations["backward"].append(('malloc', '++'))
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_order_violation(mascm))

        self.assertEqual(2, len(result))

        self.assertEqual(mascm.operations[7], result[0][0])
        self.assertEqual(mascm.operations[21], result[0][1])
        self.assertEqual(mascm.resources[0], result[0][2])

        self.assertEqual(mascm.operations[7], result[1][0])
        self.assertEqual(mascm.operations[15], result[1][1])
        self.assertEqual(mascm.resources[0], result[1][2])
