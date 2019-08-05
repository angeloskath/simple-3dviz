"""A scene defines the type of framebuffer to create and allows manipulation of
the programs uniforms, such as the camera position and light."""


import moderngl
import numpy as np
from pyrr import Matrix44, Vector3


class BaseScene(object):
    """Base scene holds the opengl context and defines utilities that will be
    useful for all scenes.
    
    Arguments
    ---------
        size: (width, height) of the framebuffer
        background: The color of the background frame buffer
        ctx: A moderngl context or None to create a standalone context
    """
    def __init__(self, size=(256, 256), background=(1, 1, 1, 1), ctx=None):
        if ctx is None:
            self._ctx = moderngl.create_standalone_context()
        else:
            self._ctx = ctx
        self._framebuffer = self._ctx.framebuffer(
            self._ctx.renderbuffer(size),
            self._ctx.depth_renderbuffer(size)
        )
        self._background = background

        self._renderables = dict()

    @property
    def renderables(self):
        return self._renderables.values()

    def add(self, renderable):
        if renderable not in self._renderables:
            renderable.init(self._ctx)
            self._renderables[renderable] = renderable

    def remove(self, renderable):
        if renderable in self._renderables:
            del self._renderables[renderable]

    @property
    def uniforms(self):
        """Return list of tuples with uniform name and value provided by the
        scene."""
        return []

    def render(self):
        # Update the uniforms
        uniforms = self.uniforms
        for r in self.renderables:
            r.update_uniforms(uniforms)

        # Render the scene
        self._framebuffer.use()
        self._ctx.enable(moderngl.DEPTH_TEST)
        self._ctx.clear(*self._background)
        for r in self.renderables:
            r.render()

    @property
    def frame(self):
        return np.frombuffer(
            self._framebuffer.read(components=4),
            dtype=np.uint8
        ).reshape(*(self._framebuffer.size + (4,)))


class Scene(BaseScene):
    def __init__(self, size=(256, 256), background=(1, 1, 1, 1), ctx=None):
        super(Scene, self).__init__(size, background, ctx)

        self._uniforms = dict(
            time=0,
            light=Vector3(dtype="float32"),
            mvp=Matrix44(dtype="float32")
        )

    @property
    def uniforms(self):
        return list(self._uniforms.items())
