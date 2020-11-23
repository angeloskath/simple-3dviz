"""This module defines and implements the Trajectory interface which provides a
way to generate a sequence of values for use with behaviours. For instance we
can generate quadratic bezier trajectories for moving the camera or lights."""

from bisect import bisect_right

import numpy as np
from pyrr import matrix33


class Trajectory(object):
    """The main trajectory interface takes a percentage and provides a
    value (most often 3d position but also color etc.)."""
    def get_value(self, t):
        """Given t in [0, 1] return the value of the trajectory. Some
        trajectories are periodic which means they support t > 1."""
        raise NotImplementedError()


class StartStopTrajectory(Trajectory):
    """Start and stop the decorated trajectory for the given values of t by
    mapping the interval to 0-1 and everything outside the interval to either 0
    or 1."""
    def __init__(self, trajectory, start=0.0, stop=1.0):
        self._trajectory = trajectory
        self._start = start
        self._stop = stop

    def get_value(self, t):
        tt = (t - self._start) / (self._stop - self._start)
        return self._trajectory.get_value(min(1.0, max(0.0, tt)))


class Linear(Trajectory):
    """From a to b the fastest way possible :-)."""
    def __init__(self, a, b):
        self._a = a
        self._b = b

    def get_value(self, t):
        if not (0 <= t <= 1):
            raise ValueError(("Linear trajectory is defined only for "
                              "t in [0, 1]"))

        return self._a + t * (self._b - self._a)


class Join(Trajectory):
    """Join several trajectories into one large trajectory using a fixed
    percentage for each.

    The passed in trajectories should be tuples of weight, trajectory. For
    instance:

        t = Join([
            (0.1, Linear(0, 1)),
            (0.5, Linear(1, 0)),
            (0.1, Linear(0, -1)),
            (0.5, Linear(-1, 0))
        ])

    NOTE: The weights don't have to sum to 1.
    """
    def __init__(self, trajectories):
        self._weights = [t[0] for t in trajectories]
        for i in range(1, len(self._weights)):
            self._weights[i] = self._weights[i] + self._weights[i-1]
        self._trajectories = [t[1] for t in trajectories]
        if not all(isinstance(t, Trajectory) for t in self._trajectories):
            raise ValueError(("The trajectories passed should implement the "
                              "Trajectory interface"))

    def get_value(self, t):
        if not (0 <= t <= 1):
            raise ValueError(("Join trajectory is defined only for "
                              "t in [0, 1]"))

        # Find the correct trajectory
        w = t*self._weights[-1]
        index = bisect_right(self._weights, w)
        if index == len(self._trajectories):
            return self._trajectories[-1].get_value(1.)

        # Find the completion percentage of that trajectory
        max_weight = self._weights[index]
        prev_weight = 0. if index==0 else self._weights[index-1]
        new_t = (w-prev_weight)/(max_weight-prev_weight)

        return self._trajectories[index].get_value(new_t)


class Repeat(Trajectory):
    """Repeat a trajectory assuming that the end point is the same as the start
    point.

    For instance can be used with Lines as follows:

        Repeat(Lines([0, 0, 0], [0, 1, 0], [1, 1, 0], [1, 0, 0], [0, 0, 0]))
    """
    def __init__(self, trajectory):
        self._trajectory = trajectory

    def get_value(self, t):
        return self._trajectory.get_value(t % 1)


class BackAndForth(Trajectory):
    """Run a trajectory forwards and backwards continuously."""
    def __init__(self, trajectory):
        self._trajectory = trajectory

    def get_value(self, t):
        t = t % 2
        return self._trajectory.get_value(2-t if t > 1 else t)


class Circle(Trajectory):
    """Circle implements a clockwise circular trajectory in 3d space.

    The circle is defined by the center, a 3d point and a normal vector. The
    start of the circle is the 3d point that rotates around the normal
    vector.
    """
    def __init__(self, center, point, normal):
        self._center = np.asarray(center, dtype=np.float64)
        self._point = np.asarray(point, dtype=np.float64)
        self._normal = np.asarray(normal, dtype=np.float64)
        radial = self._point - self._center

        cosangle = (
            self._normal.dot(radial) /
            np.sqrt(self._normal.dot(self._normal)) /
            np.sqrt(radial.dot(radial))
        )
        if cosangle > 0.01:
            raise ValueError(("The radial vector and the normal vector "
                              "are not perpendicular thus do not define "
                              "a circle"))

    def get_value(self, t):
        R = matrix33.create_from_axis_rotation(self._normal, 2*t*np.pi)
        return self._center + R.dot(self._point-self._center)


class QuadraticBezier(Trajectory):
    """A simple quadratic bezier curve.

    https://en.wikipedia.org/wiki/B%C3%A9zier_curve
    """
    def __init__(self, A, B, C):
        self._A = A
        self._B = B
        self._C = C

    def get_value(self, t):
        if not (0 <= t <= 1):
            raise ValueError(("QuadraticBezier trajectory is defined only for "
                              "t in [0, 1]"))

        return (1-t)**2 * self._A + 2*(1-t)*t * self._B + t**2 * self._C


def Lines(*points):
    """Lines is a helper function to create joins of linear trajectories.

    Lines accepts points as positional arguments or as a single iterable. The
    arguments are cast to numpy arrays and then a trajectory is created.
    """
    if len(points) > 1:
        points = np.asarray(points, dtype=np.float64)
    else:
        points = np.asarray(points[0], dtype=np.float64)

    assert len(points) > 1, "Lines expects at least two points"

    return Join([
        (1., Linear(points[i], points[i+1]))
        for i in range(len(points)-1)
    ])


def QuadraticBezierCurves(*points):
    """QuadraticBezierCurves is a helper function to create joins of quadratic
    bezier curves.

    Same as Lines it accepts points either as positional arguments or a single
    iterable.
    """
    if len(points) > 1:
        points = np.asarray(points, dtype=np.float64)
    else:
        points = np.asarray(points[0], dtype=np.float64)

    assert len(points) > 2, "QuadraticBezierCurves expects at least 3 points"
    assert (len(points) % 2) == 1, ("QuadraticBezierCurves expects an odd "
                                    "number of points")

    return Join([
        (1., QuadraticBezier(points[i], points[i+1], points[i+2]))
        for i in range(0, len(points)-2, 2)
    ])
