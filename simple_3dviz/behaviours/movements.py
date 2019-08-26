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


class _TrajectoryMovement(Behaviour):
    """Abstract class that implements adjusting a quantity based on a passed
    trajectory.

    Arguments
    ---------
        trajectory: The Trajectory object that provides values
        speed: percentage of completion per tick
    """
    def __init__(self, trajectory, speed=0.01):
        self._trajectory = trajectory
        self._speed = speed
        self._t = 0.0

    def behave(self, params):
        v = self._trajectory.get_value(self._t)
        self._t += self._speed
        self._adjust(params, v)

    def _adjust(self, params, v):
        raise NotImplementedError()


class CameraTrajectory(_TrajectoryMovement):
    """Move the camera along a trajectory."""
    def _adjust(self, params, v):
        params.scene.camera_position = v
        params.refresh = True


class LightTrajectory(_TrajectoryMovement):
    """Move the light along a trajectory."""
    def _adjust(self, params, v):
        params.scene.light = v
        params.refresh = True
