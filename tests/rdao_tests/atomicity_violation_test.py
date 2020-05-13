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
from rdao import detect_atomicity_violation
from tests.test_base import TestBase
import unittest


class DetectAtomicityViolationTest(unittest.TestCase, TestBase):
    def tearDown(self) -> None:
        super(DetectAtomicityViolationTest, self).tearDown()
        c.relations["forward"] = []
        c.relations["backward"] = []
        c.relations["symmetric"] = []

    def test_atomicity_violation1(self):
        file_to_parse = "atomicity_violation1.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        c.relations["symmetric"].append(('++', 'printf'))
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_atomicity_violation(mascm))

        self.assertEqual(2, len(result))
        # First thread
        self.assertEqual(mascm.edges[16], result[0][0][0])
        self.assertEqual(mascm.edges[23], result[0][0][1])
        self.assertEqual(mascm.edges[35], result[0][0][2])
        self.assertEqual(mascm.edges[42], result[0][0][3])
        # Second thread
        self.assertEqual(mascm.edges[35], result[1][0][0])
        self.assertEqual(mascm.edges[42], result[1][0][1])
        self.assertEqual(mascm.edges[16], result[1][0][2])
        self.assertEqual(mascm.edges[23], result[1][0][3])

    def test_atomicity_violation2(self):
        file_to_parse = "atomicity_violation2.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        c.relations["symmetric"].append(('++', 'printf'))
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_atomicity_violation(mascm))

        self.assertEqual(1, len(result))
        # First thread
        self.assertEqual(mascm.edges[16], result[0][0][0])
        self.assertEqual(mascm.edges[26], result[0][0][1])
        self.assertEqual(mascm.edges[41], result[0][0][2])

    def test_atomicity_violation3(self):
        file_to_parse = "atomicity_violation3.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        c.relations["symmetric"].append(('++', 'printf'))
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_atomicity_violation(mascm))

        self.assertEqual(1, len(result))
        # First thread
        self.assertEqual(mascm.edges[18], result[0][0][0])
        self.assertEqual(mascm.edges[34], result[0][0][1])
        self.assertEqual(mascm.edges[49], result[0][0][2])

    def test_atomicity_violation4(self):
        file_to_parse = "atomicity_violation4.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        c.relations["symmetric"].append(('++', 'printf'))
        c.relations["symmetric"].append(('--', 'printf'))
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_atomicity_violation(mascm))

        self.assertEqual(2, len(result))
        # First thread
        self.assertEqual(mascm.edges[20], result[0][0][0])
        self.assertEqual(mascm.edges[29], result[0][0][1])
        self.assertEqual(mascm.edges[37], result[0][0][2])

        self.assertEqual(mascm.edges[22], result[1][0][0])
        self.assertEqual(mascm.edges[31], result[1][0][1])
        self.assertEqual(mascm.edges[39], result[1][0][2])

    def test_atomicity_violation5(self):
        file_to_parse = "atomicity_violation5.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        c.relations["symmetric"].append(('++', 'printf'))
        c.relations["symmetric"].append(('--', 'printf'))
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_atomicity_violation(mascm))

        self.assertEqual(2, len(result))
        # First thread
        self.assertEqual(mascm.edges[20], result[0][0][0])
        self.assertEqual(mascm.edges[31], result[0][0][1])
        self.assertEqual(mascm.edges[37], result[0][0][2])

        self.assertEqual(mascm.edges[22], result[1][0][0])
        self.assertEqual(mascm.edges[33], result[1][0][1])
        self.assertEqual(mascm.edges[39], result[1][0][2])

    def test_atomicity_violation5_with_forward_relation(self):
        file_to_parse = "atomicity_violation5.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        c.relations["forward"].append(('++', 'printf'))
        c.relations["forward"].append(('--', 'printf'))
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_atomicity_violation(mascm))

        self.assertEqual(2, len(result))
        # First thread
        self.assertEqual(mascm.edges[20], result[0][0][0])
        self.assertEqual(mascm.edges[31], result[0][0][1])
        self.assertEqual(mascm.edges[37], result[0][0][2])

        self.assertEqual(mascm.edges[22], result[1][0][0])
        self.assertEqual(mascm.edges[33], result[1][0][1])
        self.assertEqual(mascm.edges[39], result[1][0][2])

    def test_no_atomicity_violation1(self):
        file_to_parse = "no_atomicity_violation1.c"
        file_path = join(self.source_path_prefix, file_to_parse)
        c.relations["symmetric"].append(('++', 'printf'))
        with purify(file_path) as pure_file_path:
            ast = parse_file(pure_file_path)
            mascm = create_mascm(deque([ast]))
        result = list(detect_atomicity_violation(mascm))

        self.assertEqual(0, len(result))
        self.assertListEqual([], result)


if "__main__" == __name__:
    unittest.main()
