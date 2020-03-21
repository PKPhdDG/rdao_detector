#!/usr/bin/env python3.7

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.2"

from helpers.path import get_project_path
from os.path import join


class TestBase:
    """ Class which is tests base """
    project_dir = get_project_path()
    source_path_prefix = join(project_dir, "tests\\example_c_sources")
    multiple_files_app_path_prefix = join(source_path_prefix, "multiple_files_apps")
