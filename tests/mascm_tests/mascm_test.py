#!/usr/bin/env python3.8

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

from mascm import MultithreadedApplicationSourceCodeModel, Relations
import unittest


class MultithreadedApplicationSourceCodeModelTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mam = MultithreadedApplicationSourceCodeModel({}, [], {}, {}, {}, {}, Relations())

    def test_get_attribute_by_full_name(self):
        self.assertDictEqual({}, self.mam.threads)
        self.assertListEqual([], self.mam.time_units)
        self.assertDictEqual({}, self.mam.resources)
        self.assertDictEqual({}, self.mam.operations)
        self.assertDictEqual({}, self.mam.mutexes)
        self.assertDictEqual({}, self.mam.edges)
        self.assertEqual(str(Relations()), str(self.mam.relations))

    def test_get_attribute_by_shortcut(self):
        self.assertDictEqual({}, self.mam.t)
        self.assertListEqual([], self.mam.u)
        self.assertDictEqual({}, self.mam.r)
        self.assertDictEqual({}, self.mam.o)
        self.assertDictEqual({}, self.mam.q)
        self.assertDictEqual({}, self.mam.f)
        self.assertEqual(str(Relations()), str(self.mam.b))


if "__main__" == __name__:
    unittest.main()
