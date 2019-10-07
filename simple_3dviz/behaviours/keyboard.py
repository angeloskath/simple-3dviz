
from ..utils import save_frame
from . import Behaviour


class SnapshotOnKey(Behaviour):
    """Save a snapshot when a key is pressed.
    
    Arguments
    ---------
        path: The path to save the images with the optional index for the
              snapshot (ie. snapshot_{}.png)
        keys: A set of keys that must all be pressed to save the frame.
              Available special keys are <ctrl>, <cmd>, <alt>, etc.
    """
    def __init__(self, path="snapshot_{:03d}.png", keys={"S"}):
        self._path = path
        self._keys = keys
        self._i = 0

    def behave(self, params):
        if params.keyboard.keys_down & self._keys == self._keys:
            frame = params.frame()
            path = self._path.format(self._i)
            self._i += 1
            save_frame(path, frame)
