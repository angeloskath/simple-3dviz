
import numpy as np
from simple_3dviz import Spherecloud
from simple_3dviz.behaviours.misc import LightToCamera
from simple_3dviz.behaviours.movements import CameraTrajectory, LightTrajectory
from simple_3dviz.behaviours.trajectory import Circle, Repeat, BackAndForth, \
    Lines, QuadraticBezierCurves
from simple_3dviz.window import show


if __name__ == "__main__":
    # Make a random point cloud
    centers = np.random.randn(30, 3)
    colors = np.array([[1., 0, 0, 1],
                       [0, 1, 1, 1]])[np.random.randint(0, 2, size=30)]
    sizes = np.ones(30)*0.2


    # Move in a circle around the points
    show(
        Spherecloud(centers, colors, sizes),
        behaviours=[
            CameraTrajectory(
                Circle([0, 0, 3], [3, 3, 3], [0, 0, 1]),
                speed=0.001
            ),
            LightToCamera(offset=[-1, -1, 0])
        ]
    )

    # Move in an endless square
    show(
        Spherecloud(centers, colors, sizes),
        behaviours=[
            CameraTrajectory(
                Repeat(Lines(
                    [-4, -4, 1],
                    [-4,  4, 1],
                    [ 4,  4, 1],
                    [ 4, -4, 1],
                    [-4, -4, 1])),
                speed=0.001
            ),
            LightToCamera(offset=[-1, -1, 0])
        ]
    )

    # Move back and forth on a line
    show(
        Spherecloud(centers, colors, sizes),
        behaviours=[
            CameraTrajectory(
                BackAndForth(Lines(
                    [-4, -4, -2],
                    [ 4, -4,  2]
                )),
                speed=0.001
            ),
            LightToCamera(offset=[-1, -1, 0])
        ]
    )

    # Move with some bezier curves
    # NOTE: Since the control points do not form lines we still got corners.
    #       If every 2nd, 3rd, 4th point form a line then the whole motion will
    #       be smooth.
    show(
        Spherecloud(centers, colors, sizes),
        behaviours=[
            CameraTrajectory(
                Repeat(QuadraticBezierCurves(
                    [-4, -4, 1],
                    [-6,  0, 1],
                    [-4,  4, 1],
                    [ 0,  6, 1],
                    [ 4,  4, 1],
                    [ 6,  0, 1],
                    [ 4, -4, 1],
                    [ 0, -6, 1],
                    [-4, -4, 1])),
                speed=0.001
            ),
            LightToCamera(offset=[-1, -1, 0])
        ]
    )

    # Let's move the light
    show(
        Spherecloud(centers, colors, sizes),
        camera_position=(3, 3, 3),
        behaviours=[
            LightTrajectory(
                Circle([0, 0, 0], [2, -4, 2], [1, 1, 1]),
                speed=0.005
            ),
        ]
    )

