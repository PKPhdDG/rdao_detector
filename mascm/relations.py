__author__ = "Damian Giebas"
__email__ = "damian.giebas@gmail.com"
__license__ = "GNU/GPLv3"
__version__ = "1.1"


class Relations:
    """Class is container of relations"""
    __slots__ = ('forward', 'backward', 'symmetric')

    def __init__(self, **kwargs):
        self.backward = []
        self.forward = []
        self.symmetric = []
        for key, value in kwargs.items():
            if hasattr(self, key):
                getattr(self, key).extend(value)

    def __repr__(self):
        return f"(forward={self.forward}, backward={self.backward}, symmetric={self.symmetric})"
