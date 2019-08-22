from ..utils import save_frame
from . import Behaviour


class SaveFrames(Behaviour):
    def __init__(self, path):
        self._path = path
        self._i = 0

    def behave(self, params):
        frame = params.scene.frame
        path = self._path.format(self._i)
        self._i += 1

        save_frame(path, frame)
