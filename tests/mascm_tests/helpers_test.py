#!/usr/bin/env python3.8

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

from helpers.path import collect_c_project_files, get_project_path
from helpers.purifier import purify, purify_file
from os.path import getsize, join
from os import remove
import unittest


class HelpersTest(unittest.TestCase):
    project_dir = get_project_path()
    source_path_prefix = join(project_dir, "tests/example_c_sources")
    multiple_files_app_path_prefix = join(source_path_prefix, "multiple_files_apps")

    def test_purify_file_with_path_to_file(self):
        expected_file_size: int = 5411
        file_to_parse: str = "single_thread_for_loop.c"
        file_path: str = join(self.source_path_prefix, file_to_parse)
        pure_file_path: str = purify_file(file_path)
        self.assertEqual(f"{file_path}.pure", pure_file_path)
        file_size: int = getsize(pure_file_path)
        self.assertEqual(expected_file_size, file_size)
        remove(pure_file_path)

    def test_purify_with_path_to_file(self):
        expected_file_size: int = 5411
        file_to_parse: str = "single_thread_for_loop.c"
        file_path: str = join(self.source_path_prefix, file_to_parse)
        with purify(file_path) as pure_file_path:
            self.assertEqual(f"{file_path}.pure", pure_file_path)
            file_size: int = getsize(pure_file_path)
            self.assertEqual(expected_file_size, file_size)

    def test_purify_file_with_path_to_dir(self):
        file_to_parse: str = "multiple_files_apps"
        file_path: str = join(self.source_path_prefix, file_to_parse)
        with self.assertRaises(IsADirectoryError):
            purify_file(file_path)

    def test_purify_file_with_path_to_non_exist_file(self):
        file_to_parse: str = "single_thread.c"
        file_path: str = join(self.source_path_prefix, file_to_parse)
        with self.assertRaises(FileNotFoundError):
            purify_file(file_path)

    def test_collect_c_files_from_dir(self):
        dir_path = join(self.multiple_files_app_path_prefix, "1")
        self.assertEqual(3, len(list(collect_c_project_files(dir_path))))


if "__main__" == __name__:
    unittest.main()
