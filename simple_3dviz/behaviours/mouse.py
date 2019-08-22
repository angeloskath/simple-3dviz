import numpy as np
from pyrr import Vector3, matrix44, vector

from . import Behaviour


class MouseRotate(Behaviour):
    """Rotate the view based using the mouse when left button is pressed."""
    def __init__(self):
        self._start = None
        self._rot = None
        self._camera_right = None
        self._camera_up = None

    def behave(self, params):
        if params.mouse.left_pressed:
            if self._start is None:
                self._start = params.mouse.location
                self._rot = params.scene.rotation
                cam_position, w = Vector3.from_vector4(params.scene.vm[3])
                cam_position /= w
                cam_target = params.scene.camera_target
                cam_up = params.scene.up_vector
                inv_cam_dir = vector.normalize(cam_position-cam_target)
                self._camera_right = np.cross(cam_up, inv_cam_dir)
                self._camera_up = np.cross(inv_cam_dir, self._camera_right)
            else:
                size = params.scene.size
                end = params.mouse.location
                deltaX = float(end[0] - self._start[0])/size[0]
                deltaY = float(end[1] - self._start[1])/size[1]

                rx = matrix44.create_from_axis_rotation(
                    axis=self._camera_up,
                    theta=deltaX * np.pi
                )
                ry = matrix44.create_from_axis_rotation(
                    axis=self._camera_right,
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

