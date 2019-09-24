from ..utils import save_frame
from . import Behaviour


class SaveFrames(Behaviour):
    def __init__(self, path, every_n=1):
        self._path = path
        self._every_n = every_n
        self._i = 0

    def behave(self, params):
        frame = params.frame()
        path = self._path.format(self._i)
        self._i += 1

        if (self._i % self._every_n) == 0:
            save_frame(path, frame)
