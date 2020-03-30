# Overview

simple-3dviz provides a set of functionalities that implement the `Behaviour`
interface that can be used for modelling the various changes in the scene that are
unrelated to the scene management (e.g. creation, rendering etc.). For example, it
implements various behaviours for animations, mouse interactions etc.

## Movements and Trajectories

In simple-3dviz, it is possible to move the camera and the light based a
trajectory that can be a circle, a bezier curve or a line.

```python
>>> from simple_3dviz import Spherecloud
>>> from simple_3dviz.window import show
>>> from simple_3dviz.behaviours.misc import LightToCamera
>>> from simple_3dviz.behaviours.movements import CameraTrajectory, LightTrajectory
>>> from simple_3dviz.behaviours.trajectory import Circle, Repeat, BackAndForth, \
...    Lines, QuadraticBezierCurves
>>> import numpy as np
>>> import matplotlib.pyplot as plt
>>> t = np.linspace(0, 4 * np.pi, 20)
>>> x = np.sin(2 * t)
>>> y = np.cos(t)
>>> z = np.cos(2 * t)
>>> sizes = (2 + np.sin(t)) * 0.125
>>> centers = np.stack([x, y, z]).reshape(3, -1).T
>>> cmap = plt.cm.jet
>>> colors = cmap(np.random.choice(np.arange(500), centers.shape[0]))

# Move in a circle around the points
>>> show(
>>>     Spherecloud(centers, colors, sizes),
>>>     behaviours=[
>>>         CameraTrajectory(
>>>             Circle([0, 0, 3], [3, 3, 3], [0, 0, 1]),
>>>             speed=0.01
>>>         ),
>>>         LightToCamera(offset=[-1, -1, 0]),
>>>     ]
>>> )

# Move in an endless square
>>> show(
>>>     Spherecloud(centers, colors, sizes),
>>>     behaviours=[
>>>         CameraTrajectory(
>>>             Repeat(Lines(
>>>                 [-4, -4, 1],
>>>                 [-4,  4, 1],
>>>                 [ 4,  4, 1],
>>>                 [ 4, -4, 1],
>>>                 [-4, -4, 1])),
>>>             speed=0.01
>>>         ),
>>>         LightToCamera(offset=[-1, -1, 0])
>>>     ]
>>> )

# Move with some bezier curves
>>> show(
>>>     Spherecloud(centers, colors, sizes),
>>>     behaviours=[
>>>         CameraTrajectory(
>>>             Repeat(QuadraticBezierCurves(
>>>                 [-4, -4, 1],
>>>                 [-6,  0, 1],
>>>                 [-4,  4, 1],
>>>                 [ 0,  6, 1],
>>>                 [ 4,  4, 1],
>>>                 [ 6,  0, 1],
>>>                 [ 4, -4, 1],
>>>                 [ 0, -6, 1],
>>>                 [-4, -4, 1])),
>>>             speed=0.001
>>>         ),
>>>         LightToCamera(offset=[-1, -1, 0])
>>>     ]
>>> )
```

<div style="text-align: center;">
    <img src="../img/animations_camera_circle.gif" alt="Animations 1" width=32.5% height=50%/>
    <img src="../img/animations_camera_square.gif" alt="Animations 2" width=32.5% height=50%/>
    <img src="../img/animations_camera_bezier_curve.gif" alt="Animations 3" width=32.5% height=50%/>
</div>

## Keyboard and mouse interactions

When using the scene viewer via the `show()` fuction, it is possible to
perform various actions either using the mouse of the keybord.

- Rotate: Press the left button click
- Pan: Press the middle button click
- Zoom in/out: Scroll the mouse wheel

The available keyboard commands are:

- `SnapshotOnKey`: Allows you to take a snapshot of the scene when a key is
  pressed.
- `CameraReport`: Reports the camera position, its vieweing direction and the the 3d
  direction that indicates which direction is "up" at the current timestamp.
- `SortTriangles`: Make sure that the triangles will be sorted so that the transparency
  works as well.
