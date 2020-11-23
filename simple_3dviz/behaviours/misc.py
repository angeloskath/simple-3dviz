
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


class AddObjectsSequentially(Behaviour):
    """Add a series of objects to a scene at constant time intervals.

    Arguments
    ---------
        objects: A list of Renderable objects
        interval: The interval between additions of objects in ticks
    """
    def __init__(self, objects, interval=30):
        self._objects = objects
        self._interval = interval

        self._ticks = interval
        self._index = len(objects)

    def behave(self, params):
        self._ticks += 1
        if self._ticks > self._interval:
            self._ticks = 0
            if self._index >= len(self._objects):
                for o in self._objects:
                    params.scene.remove(o)
                self._index = 0
            params.scene.add(self._objects[self._index])
            self._index += 1
            params.refresh = True


class CycleThroughObjects(Behaviour):
    """Add a set of objects to the scene removing the ones previously added.

    Arguments
    ---------
        objects: A list of lists of Renderable objects
        interval: The interval between additions and removals in ticks
    """
    def __init__(self, objects, interval=30):
        self._objects = objects
        self._interval = interval

        self._ticks = interval
        self._object = -1

    def behave(self, params):
        self._ticks += 1
        if self._ticks > self._interval:
            self._ticks = 0
            for o in self._objects[self._object]:
                params.scene.remove(o)
            self._object = (self._object + 1) % len(self._objects)
            for o in self._objects[self._object]:
                params.scene.add(o)
            params.refresh = True


class SortTriangles(Behaviour):
    """Sort the triangles of the scene wrt the camera position."""
    def __init__(self):
        self._prev_camera = None

    def behave(self, params):
        camera = params.scene.camera_position
        if (
            self._prev_camera is None or
            any([
                abs(c1-c2)>1e-3 for c1, c2 in zip(self._prev_camera, camera)
            ])
        ):
            self._prev_camera = camera
            for r in params.scene.renderables:
                if hasattr(r, "sort_triangles"):
                    r.sort_triangles(camera)
            params.refresh = True


class StartStopBehaviour(Behaviour):
    """Start and stop the decorated behaviour for the given frame counts."""
    def __init__(self, behaviour, start=0, stop=100):
        self._cnt = 0
        self._behaviour = behaviour
        self._start = start
        self._stop = stop

    def behave(self, params):
        self._cnt += 1
        if self._stop >= self._cnt > self._start:
            return self._behaviour.behave(params)
