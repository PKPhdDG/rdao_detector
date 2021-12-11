__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "1.1"

from os.path import dirname
from pathlib import Path


def get_project_path() -> str:
    """ Function return path to main project directory
    :return: String with path
    """
    return Path(dirname(__file__)).parent


def collect_c_project_files(dir_path: str, extensions: list = ("c", "h")) -> str:
    """ Coroutine which return all source codes and headers file from given path
    :param dir_path: Path with sources
    :param extensions: list with file extensions
    :return: string with path to file
    """
    dir_path = Path(dir_path)
    for extension in extensions:
        for file in dir_path.glob(f"**/*.{extension}"):
            yield str(file)
