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
