
import numpy as np

from . import Behaviour


class LightToCamera(Behaviour):
    """Move the light to the same position as the camera so that the objects
    are always lit."""
    def __init__(self, offset=[0, 0, 0]):
        self._offset = offset

    def behave(self, params):
        newpos = params.scene.camera_position + self._offset
        if np.allclose(newpos, params.scene.light):
            return

        params.scene.light = newpos
        params.refresh = True
