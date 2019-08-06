
import moderngl
import wx
import wx.glcanvas

from .base import BaseWindow, Behaviour
from ..scenes import Scene

class Window(BaseWindow):
    _FRAME_STYLE = wx.DEFAULT_FRAME_STYLE & ~(
        wx.RESIZE_BORDER | wx.MAXIMIZE_BOX
    )

    class _Frame(wx.Frame):
        """A simple frame for our wxWidgets app."""
        def __init__(self, window, size, title):
            super(Window._Frame, self).__init__(
                None,
                style=Window._FRAME_STYLE
            )
            self._window = window
            self.SetTitle(title)
            self.SetClientSize(size)
            self.Center()
            self.view = Window._Canvas(self._window, self)

    class _Canvas(wx.glcanvas.GLCanvas):
        def __init__(self, window, parent):
            super(Window._Canvas, self).__init__(
                parent,
                attribList=[
                    wx.glcanvas.WX_GL_CORE_PROFILE,
                    wx.glcanvas.WX_GL_RGBA,
                    wx.glcanvas.WX_GL_DOUBLEBUFFER
                ]
            )
            self._window = window
            self._context = wx.glcanvas.GLContext(self)
            self._mgl_context = None
            self._ticker = wx.Timer(self)

            self.Bind(wx.EVT_PAINT, self._on_paint)
            self.Bind(wx.EVT_TIMER, self._on_tick, self._ticker)

        def _on_paint(self, event):
            self.SetCurrent(self._context)
            if self._window._scene is None:
                self._mgl_context = moderngl.create_context()
                self._window._scene = Scene(
                    size=(self.Size.width, self.Size.height),
                    background=(0,)*4,
                    ctx=self._mgl_context
                )
                self._ticker.Start(16)

            self._window._draw()
            self.SwapBuffers()

        def _on_tick(self, event):
            if self._window._behave(event):
                self.Refresh()

    def __init__(self, size=(512, 512)):
        super(Window, self).__init__(size)
        self._scene = None

    def _behave(self, event):
        # Make the behaviour parameters
        params = Behaviour.Params(
            self,
            self._scene
        )

        # Run the behaviours
        remove = []
        for i, b in enumerate(self._behaviours):
            b.behave(params)
            if params.done:
                remove.append(i)
                params.done = False
            if params.stop_propagation:
                break

        # Remove the ones that asked to be removed
        for i in reversed(remove):
            self._behaviours.pop(i)

        # Return whether we should paint again
        return params.refresh

    def _draw(self):
        self._scene.render()

    def show(self, title="Scene"):
        app = wx.App(False)
        frame = self._Frame(self, self.size, title)
        frame.Show()
        app.MainLoop()
