"""Create a window with an attached scene that is rendered in real time."""

try:
    from .wx import Window
except ImportError:
    raise ImportError("No supported gui library was found. Install wxPython.")


from ..renderables import Renderable
from ..behaviours import Behaviour, SceneInit
from ..behaviours.mouse import MouseRotate, MouseZoom, MousePan
from ..behaviours.keyboard import CameraReport, SortTriangles


def simple_window(init, size=(512, 512)):
    """Return a window with the expected behaviours added.

    Arguments
    ---------
        init: callable that sets up the scene
        size: (w, h) the size of the window

    Returns
    -------
        Window instance
    """
    w = Window(size)
    w.add_behaviours([SceneInit(init), MouseRotate(), MouseZoom(),
                      MousePan(), CameraReport(), SortTriangles()])
    return w


def show(renderables, size=(512, 512), background=(1,)*4, title="Scene",
         camera_position=(-2, -2, -2), camera_target=(0, 0, 0),
         up_vector=(0, 0, 1), light=None, behaviours=[]):
    """Creates a simple window that displays the renderables.

    Arguments
    ---------
        renderables: list[Renderable] the renderables to be displayed in the
                     scene
        size: (w, h) the size of the window
        background: (r, g, b, a) the rgba tuple for the background
        title: str the title of the window
        camera_position: (x, y, z) the position of the camera
        camera_target: (x, y, z) the point that the camera looks at
        up_vector: (x, y, z) defines the floor and sky
        light: (x, y, z) defines the position of the light source
    """
    if not isinstance(renderables, (list, tuple)):
        renderables = [renderables]
    if not all(isinstance(r, Renderable) for r in renderables):
        raise ValueError(("show() expects one or more renderables as "
                          "parameters not {}").format(renderables))

    def init(scene):
        for r in renderables:
            scene.add(r)
        scene.background = background
        scene.camera_position = camera_position
        scene.camera_target = camera_target
        scene.up_vector = up_vector
        if light is not None:
            scene.light = light

    w = simple_window(init, size=size)
    w.add_behaviours(behaviours)
    w.show(title)
