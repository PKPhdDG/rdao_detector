#!/usr/bin/env python3.8

__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "1.1"

from collections import deque
import config as c
from contextlib import contextmanager
from helpers.path import get_project_path
import logging
from os import remove
from os.path import exists, isfile, join
from pathlib import Path
from subprocess import Popen, PIPE
import sys
from typing import Iterable


def purify_file(path: str, cflags: str = "", headers: Iterable[str] = tuple()) -> str:
    """ Function purify C file
    :param path: Path to C file
    :param cflags: C compiler flags needed to compilation
    :param headers: Sequence with paths to headers
    :return:  Path to pured C file
    """
    if not exists(path):
        raise FileNotFoundError(f"Given path does not exists: '{path}'")
    if not isfile(path):
        raise IsADirectoryError(f"Given path is not a file: '{path}'")
    dir_path = get_project_path()
    output_file: str = f"{path}.pure"
    command: list = [c.compiler_cmd, "-Wall", "-I", join(dir_path, "utils/fake_libc_include"), cflags]
    if headers:
        for header_path in headers:
            command.extend(["-I", header_path])
    command.extend(["-E", path])
    o, e = Popen(' '.join(command), stdout=PIPE, stderr=PIPE, shell=True).communicate()
    if e:
        logging.critical(f"Critical error during purifizing file: {path}")
        logging.critical(e)
        logging.critical("Terminating application")
        sys.exit(1)
    with open(output_file, "wb") as f:
        f.write(o)
    return output_file


def purify_files(paths: Iterable[str], cflags: str = "", header_extensions: tuple = ("h",)) -> deque:
    """ Purify set of files

    :param paths: Paths to C files
    :param cflags: C compiler flags needed to compilation
    :param header_extensions: Header files extensions
    :return:  Paths to pured C files
    """
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
        pure_files.append(purify_file(file, cflags, headers_dirs))
    return pure_files


@contextmanager
def purify(path: str) -> str:
    pure_file_path = purify_file(path)
    yield pure_file_path
    remove(pure_file_path)
