import numpy as np
from pyrr import matrix33, vector

from . import Behaviour
from .trajectory import Circle


class MouseRotate(Behaviour):
    """Rotate the camera based using the mouse when left button is pressed.

    We rotate the camera with the following convention. At any given point we
    consider a sphere with a center in target and radius equal to the distance
    to the camera. We move on that sphere based on the movements of the mouse.
    """
    def __init__(self):
        self._start = None
        self._origin = None
        self._camera_pos = None
        self._right = None
        self._up = None

    def behave(self, params):
        if params.mouse.left_pressed:
            if self._start is None:
                self._start = params.mouse.location
                self._origin = params.scene.camera_target
                self._camera_pos = params.scene.camera_position
                cam_dir = vector.normalize(self._camera_pos - self._origin)
                self._right = np.cross(params.scene.up_vector, cam_dir)
                self._up = np.cross(cam_dir, self._right)
            else:
                size = params.scene.size
                end = params.mouse.location
                deltaX = float(end[0] - self._start[0])/size[0]
                deltaY = float(end[1] - self._start[1])/size[1]

                Rx = matrix33.create_from_axis_rotation(
                    self._up,
                    deltaX*2*np.pi
                )
                Ry = matrix33.create_from_axis_rotation(
                    self._right,
                    deltaY*2*np.pi
                )
                R = Ry.dot(Rx)
                newpos = self._origin + R.dot(self._camera_pos - self._origin)
                newup = R.dot(self._up)

                params.scene.camera_position = newpos
                params.scene.up_vector = newup
                params.refresh = True
        else:
            self._start = None


class MouseZoom(Behaviour):
    """Zoom in/out with the mouse scroll wheel."""
    def __init__(self, delta=0.9):
        self._delta = delta

    def behave(self, params):
        rotations = params.mouse.wheel_rotation
        if rotations != 0:
            cam_position = params.scene.camera_position
            cam_target = params.scene.camera_target
            ray = cam_target - cam_position
            if rotations > 0:
                cam_position += ray * (1-self._delta)
            else:
                cam_position -= ray * (1-self._delta)
            params.scene.camera_position = cam_position
            params.refresh = True


class MousePan(Behaviour):
    """Move the target by dragging the mouse with the middle button pressed."""
    def __init__(self, delta=1.):
        self._delta = delta
        self._start = None
        self._target = None
        self._right = None
        self._up = None

    def behave(self, params):
        if params.mouse.middle_pressed:
            if self._start is None:
                self._start = params.mouse.location
                self._target = params.scene.camera_target
                cam_dir = params.scene.camera_position - self._target
                cam_dir = vector.normalize(cam_dir)
                self._right = np.cross(params.scene.up_vector, cam_dir)
                self._up = np.cross(cam_dir, self._right)
            else:
                size = params.scene.size
                end = params.mouse.location
                deltaX = float(end[0] - self._start[0])/size[0]
                deltaY = float(end[1] - self._start[1])/size[1]

                newtarget = (
                    self._target +
                    -self._delta * deltaX * self._right +
                    self._delta * deltaY * self._up
                )
                params.scene.camera_target = newtarget
                params.refresh = True
        else:
            self._start = None
