#!/usr/bin/env python3.8

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "1.1"

from tests.rdao_tests.atomicity_violation_test import DetectAtomicityViolationTest
from tests.rdao_tests.deadlock_test import DetectDeadlockTest
from tests.rdao_tests.order_violation_test import DetectOrderViolationTest
from tests.rdao_tests.race_condition_test import DetectRaceConditionTest
import unittest

if "__main__" == __name__:
    unittest.main()
