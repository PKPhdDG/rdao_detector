#!/usr/bin/env python3.8

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

import unittest

from tests.mascm_tests.create_mascm_test import CreateMamTest
from tests.mascm_tests.helpers_test import HelpersTest
from tests.mascm_tests.mascm_test import MultithreadedApplicationSourceCodeModelTest

if "__main__" == __name__:
    unittest.main()
