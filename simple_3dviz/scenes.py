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

        self._camera = Matrix44.perspective_projection(45., 1., 0.1, 1000.)
        self._camera_position = Vector3([-2., -2, -2])
        self._camera_target = Vector3([0., 0, 0])
        self._rotation = Matrix44.identity()
        self._up_vector = Vector3([0, 0, 1])

        self._uniforms = dict(
            light=Vector3([-0.5, -0.8, -2], dtype="float32"),
            mvp=self.mvp
        )

    @property
    def light(self):
        return self._uniforms["light"].copy()

    @light.setter
    def light(self, l):
        self._uniforms["light"][...] = l

    @property
    def mvp(self):
        lookat = Matrix44.look_at(
            self._camera_position,
            self._camera_target,
            self._up_vector
        )
        return (self._camera * lookat * self._rotation).astype(np.float32)

    @property
    def camera_matrix(self):
        return self._camera.copy()

    @camera_matrix.setter
    def camera_matrix(self, cam):
        self._camera[...] = cam
        self._uniforms["mvp"] = self.mvp

    @property
    def camera_position(self):
        return self._camera_position.copy()

    @camera_position.setter
    def camera_position(self, pos):
        self._camera_position[...] = pos
        self._uniforms["mvp"] = self.mvp

    @property
    def camera_target(self):
        return self._camera_target.copy()

    @camera_target.setter
    def camera_target(self, target):
        self._camera_target[...] = target
        self._uniforms["mvp"] = self.mvp

    @property
    def up_vector(self):
        return self._up_vector.copy()

    @up_vector.setter
    def up_vector(self, up):
        self._up_vector[...] = up
        self._uniforms["mvp"] = self.mvp

    @property
    def rotation(self):
        return self._rotation.copy()

    @rotation.setter
    def rotation(self, rot):
        self._rotation[...] = rot
        self._uniforms["mvp"] = self.mvp

    def rotate_x(self, angle):
        self._rotation *= Matrix44.from_x_rotation(angle)
        self._uniforms["mvp"] = self.mvp

    def rotate_y(self, angle):
        self._rotation *= Matrix44.from_y_rotation(angle)
        self._uniforms["mvp"] = self.mvp

    def rotate_z(self, angle):
        self._rotation *= Matrix44.from_z_rotation(angle)
        self._uniforms["mvp"] = self.mvp

    @property
    def uniforms(self):
        return list(self._uniforms.items())
