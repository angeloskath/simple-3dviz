import time

import numpy as np

from . import Behaviour


class RotateModel(Behaviour):
    """Rotate all the models around an axis with a given speed (radians per
    tick).
    
    Arguments
    ---------
        axis: {'x', 'y', 'z'}
        speed: float, radians per tick
    """
    def __init__(self, axis='z', speed=np.pi/90):
        self._function = dict(
            x=lambda s, a: s.rotate_x(a),
            y=lambda s, a: s.rotate_y(a),
            z=lambda s, a: s.rotate_z(a)
        )[axis]
        self._speed = speed

    def behave(self, params):
        self._function(params.scene, self._speed)
        params.refresh = True
