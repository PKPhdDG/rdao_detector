#!/usr/bin/env python3

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"

from contextlib import contextmanager
from os import remove
from os.path import dirname, exists, isfile, join
from pathlib import Path
from subprocess import run


def purify_file(path: str) -> str:
    """ Function purify C file
    :param path: Path to C file
    :return:  Path to pure C file
    """
    if not exists(path):
        raise FileNotFoundError(f"Given path does not exists: '{path}'")
    if not isfile(path):
        raise IsADirectoryError(f"Given path is not a file: '{path}'")
    dir_path = Path(dirname(__file__)).parent
    output_file: str = f"{path}.pure"
    command: list = ["gcc.exe", "-Wall", "-I", join(dir_path, "utils/fake_libc_include"), "-E", path, ">", output_file]
    run(command, check=True, shell=True)
    return output_file


@contextmanager
def purify(path: str) -> str:
    pure_file_path = purify_file(path)
    yield pure_file_path
    remove(pure_file_path)
