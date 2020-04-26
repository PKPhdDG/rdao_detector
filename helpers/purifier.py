#!/usr/bin/env python3.8

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.4"

from collections import deque
from contextlib import contextmanager
from helpers.path import get_project_path
from os import remove
from os.path import exists, isfile, join
from pathlib import Path
from subprocess import run
from typing import Iterable


def purify_file(path: str, headers: Iterable[str] = tuple()) -> str:
    """ Function purify C file
    :param path: Path to C file
    :param headers: Sequence with paths to headers
    :return:  Path to pure C file
    """
    if not exists(path):
        raise FileNotFoundError(f"Given path does not exists: '{path}'")
    if not isfile(path):
        raise IsADirectoryError(f"Given path is not a file: '{path}'")
    dir_path = get_project_path()
    output_file: str = f"{path}.pure"
    command: list = ["gcc.exe", "-Wall", "-I", join(dir_path, "utils/fake_libc_include")]
    if headers:
        for header_path in headers:
            command.extend(["-I", header_path])
    command.extend(["-E", path, ">", output_file])
    run(command, check=True, shell=True)
    return output_file


def purify_files(paths: Iterable[str], header_extensions: tuple = ("h",)) -> deque:
    headers_dirs = set()
    source_files = list()
    pure_files = deque()
    for file in paths:
        *_, extension = str(file).split(".")
        if extension in header_extensions:
            headers_dirs.add(str(Path(file).absolute().parent))
        else:
            source_files.append(str(Path(file).absolute()))
    for file in source_files:
        pure_files.append(purify_file(file, headers_dirs))
    return pure_files


@contextmanager
def purify(path: str) -> str:
    pure_file_path = purify_file(path)
    yield pure_file_path
    remove(pure_file_path)
