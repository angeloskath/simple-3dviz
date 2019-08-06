"""Create a window with an attached scene that is rendered in real time."""

try:
    from .wx import Window
except ImportError:
    raise ImportError("No supported gui library was found. Install wxPython.")
