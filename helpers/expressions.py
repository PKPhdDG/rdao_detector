#!/usr/bin/env python3.8

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "1.1"

import re

usage_edge_exp = re.compile(r"\(o\d+,\d+, r\d+\)")
dependency_edge_exp = re.compile(r"\(r\d+, o\d+,\d+\)")
transition_edge_exp = re.compile(r"\(o\d+,\d+, o\d+,\d+\)")
mutex_exp = re.compile(r"q\d+")
mutex_lock_edge_exp = re.compile(r"\(q\d+, o\d+,\d+\)")
mutex_unlock_edge_exp = re.compile(r"\(o\d+,\d+, q\d+\)")
operation_exp = re.compile(r"o\d+,\d+")
resource_exp = re.compile(r"r\d+")
