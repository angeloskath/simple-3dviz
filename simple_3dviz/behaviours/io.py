from PIL import Image

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
        self._i += 1

        if (self._i % self._every_n) != 0:
            return

        frame = params.frame()
        path = self._path.format(self._i)
        save_frame(path, frame)


class SaveGif(Behaviour):
    """Save the rendered frames to a GIF animation.

    Arguments
    ---------
        path: Path to the file to save the gif animation
        every_n: int, save every n frames instead of all frames (default: 1)
        duration: int, the display duration in milliseconds per frame
                  (default: 16*every_n)
        loop: int, number of times the gif should loop (default: 0 which means
                   for ever)
        optimize: bool, whether to attempt to optimize the color pallete
                  (default: True)
    """
    def __init__(self, path, every_n=1, duration=None, loop=0, optimize=True):
        self._path = path
        self._every_n = every_n
        self._duration = duration or 16*every_n
        self._loop = loop

        self._i = 0
        self._images = []

    def behave(self, params):
        self._i += 1

        if not params.last_call and (self._i % self._every_n) != 0:
            return

        frame = params.frame()
        self._images.append(Image.fromarray(frame[::-1]))

        if params.last_call:
            self._images[0].save(
                self._path,
                save_all=True,
                append_images=self._images[1:],
                duration=self._duration,
                loop=self._loop
            )
            self._i = 0
            self._images = []
