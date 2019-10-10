
from ..utils import save_frame
from . import Behaviour


class OnKeys(Behaviour):
    """Abstract class that performs an action when a set of keys is pressed."""
    def __init__(self, keys):
        self._keys = keys
        self._act = False

    def behave(self, params):
        if params.keyboard.keys_down & self._keys == self._keys:
            self._act = True
        elif self._act and params.keyboard.keys_up | self._keys:
            self._act = False
            self.action(params)

    def action(self, params):
        raise NotImplementedError()


class SnapshotOnKey(OnKeys):
    """Save a snapshot when a key is pressed.
    
    Arguments
    ---------
        path: The path to save the images with the optional index for the
              snapshot (ie. snapshot_{}.png)
        keys: A set of keys that must all be pressed to save the frame.
              Available special keys are <ctrl>, <cmd>, <alt>, etc.
    """
    def __init__(self, path="snapshot_{:03d}.png", keys={"S"}):
        super(SnapshotOnKey, self).__init__(keys)
        self._path = path
        self._i = 0

    def action(self, params):
        frame = params.frame()
        path = self._path.format(self._i)
        self._i += 1
        save_frame(path, frame)
