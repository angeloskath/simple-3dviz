
import time

import numpy as np
from pyrr import matrix44, vector

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


class MouseRotate(Behaviour):
    """Rotate the view based using the mouse when left button is pressed.

    Arguments
    ---------
        axis_x: {0, 1, 2}, Which axis to rotate when dragging along x
        axis_y: {0, 1, 2}, Which axis to rotate when dragging along y
        dir_x: {1, -1}, Which direction to rotate when dragging along x
        dir_y: {1, -1}, Which direction to rotate when dragging along y
    """
    def __init__(self, axis_x=2, axis_y=0, dir_x=1, dir_y=1):
        self._start = None
        self._rot = None
        self._axis_x = [0, 0, 0]
        self._axis_y = [0, 0, 0]
        self._axis_x[axis_x] = float(dir_x)
        self._axis_y[axis_y] = float(dir_y)

    def behave(self, params):
        if params.mouse.left_pressed:
            if self._start is None:
                self._start = params.mouse.location
                self._rot = params.scene.rotation
            else:
                size = params.scene.size
                end = params.mouse.location
                deltaX = float(end[0] - self._start[0])/size[0]
                deltaY = float(end[1] - self._start[1])/size[1]

                rx = matrix44.create_from_axis_rotation(
                    axis=self._axis_x,
                    theta=deltaX * np.pi
                )
                ry = matrix44.create_from_axis_rotation(
                    axis=self._axis_y,
                    theta=deltaY * np.pi
                )
                params.scene.rotation = self._rot * rx * ry
                params.refresh = True
        else:
            self._start = None


class MouseZoom(Behaviour):
    """Zoom in/out with the mouse scroll wheel."""
    def __init__(self, delta=1.):
        self._delta = 1.

    def behave(self, params):
        rotations = params.mouse.wheel_rotation
        if rotations != 0:
            cam_position = params.scene.camera_position
            cam_target = params.scene.camera_target
            ray = vector.normalize(cam_target - cam_position)
            cam_position += ray * self._delta * rotations
            params.scene.camera_position = cam_position
            params.refresh = True
