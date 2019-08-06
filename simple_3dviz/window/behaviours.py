
import time

import numpy as np

from .base import Behaviour


class SceneInit(Behaviour):
    """Initialize a scene.
    
    Run an init function once and update the render.
    """
    def __init__(self, scene_init):
        self._init_func = scene_init

    def behave(self, params):
        self._init_func(params.scene)
        params.done = True
        params.stop_propagation = True
        params.refresh = True


class Rotate(Behaviour):
    """Rotate around an axis with a given speed.
    
    Arguments
    ---------
        axis: {'x', 'y', 'z'}
        speed: float, radians per second
    """
    def __init__(self, axis='z', speed=np.pi/90):
        self._function = dict(
            x=lambda s, a: s.rotate_x(a),
            y=lambda s, a: s.rotate_y(a),
            z=lambda s, a: s.rotate_z(a)
        )[axis]
        self._speed = speed
        self._prev = None

    def behave(self, params):
        # first time called so note the time
        if self._prev is None:
            self._prev = time.time()
            return

        # rotate
        now = time.time()
        elapsed = now - self._prev
        self._function(params.scene, elapsed * self._speed)
        params.refresh = True

        # swap the time
        self._prev = now
