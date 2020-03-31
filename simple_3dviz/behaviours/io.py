from ..utils import save_frame
from . import Behaviour


class SaveFrames(Behaviour):
    """Save the rendered frames to a file.

    Arguments
    ---------
        path: Path to the file to save the frame. Python's format() will be
              used to add the index of the frame in the file name as follows
              '/path/to/frame_{}.png' -> /path/to/frame_0.png .
        every_n: int, Save every n frames instead of all frames.
    """
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
