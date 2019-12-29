__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "0.1"

from os.path import dirname
from pathlib import Path


def get_project_path() -> str:
    """ Function return path to main project directory
    :return: String with path
    """
    return Path(dirname(__file__)).parent


def collect_c_project_files(dir_path: str, extensions: list = ("c", "h")) -> str:
    dir_path = Path(dir_path)
    for file in dir_path.iterdir():
        *_, extension = str(file).split(".")
        if extension in extensions:
            yield file
