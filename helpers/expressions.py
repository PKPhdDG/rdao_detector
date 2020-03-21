#!/usr/bin/env python3.7

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.2"

import re

edge_exp = re.compile(r"\(o\d+,\d+, r\d+\)")
mutex_exp = re.compile(r"q\d+")
operation_exp = re.compile(r"o\d+,\d+")
resource_exp = re.compile(r"r\d+")
