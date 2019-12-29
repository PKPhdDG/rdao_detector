#!/usr/bin/env python3

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"

from contextlib import contextmanager
import os
from subprocess import run


def purify_file(path: str) -> str:
    """ Function purify C file
    :param path: Path to C file
    :return:  Path to pure C file
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Given path does not exists: '{path}'")
    if not os.path.isfile(path):
        raise IsADirectoryError(f"Given path is not a file: '{path}'")
    output_file: str = f"{path}.pure"
    command: list = ["gcc.exe", "-Wall", "-I../utils/fake_libc_include", "-E", path, ">", output_file]
    cp = run(command, check=True, shell=True)
    return output_file

@contextmanager
def purify(path: str) -> str:
    pure_file_path = purify_file(path)
    yield pure_file_path
    os.remove(pure_file_path)
