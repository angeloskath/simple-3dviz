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
            self._ctx.enable(moderngl.BLEND)
            self._ctx.blend_func = (
                moderngl.SRC_ALPHA,
                moderngl.ONE_MINUS_SRC_ALPHA
            )
            self._framebuffer = self._ctx.framebuffer(
                self._ctx.renderbuffer(size),
                self._ctx.depth_renderbuffer(size)
            )
        else:
            self._ctx = ctx
            self._framebuffer = None

        self._background = background
        self._renderables = dict()

    @property
    def size(self):
        return self._ctx.fbo.size

    @property
    def background(self):
        return self._background

    @background.setter
    def background(self, v):
        b = list(self._background)
        for i in range(len(v)):
            b[i] = v[i]
        self._background = tuple(b)

    @property
    def renderables(self):
        return self._renderables.values()

    def add(self, renderable):
        if renderable not in self._renderables:
            renderable.init(self._ctx)
            self._renderables[renderable] = renderable

    def remove(self, renderable):
        if renderable in self._renderables:
            self._renderables[renderable].release()
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
        if self._framebuffer is not None:
            self._framebuffer.use()
        self._ctx.enable(moderngl.DEPTH_TEST)
        self._ctx.clear(*self._background)
        for r in self.renderables:
            r.render()

    @property
    def frame(self):
        if self._framebuffer is not None:
            return np.frombuffer(
                self._framebuffer.read(components=4),
                dtype=np.uint8
            ).reshape(*(self._framebuffer.size + (4,)))
        else:
            raise RuntimeError(("This scene is rendering on a framebuffer "
                                "managed by someone else (gui perhaphs). "
                                "Access the frame from there."))


class Scene(BaseScene):
    def __init__(self, size=(256, 256), background=(1, 1, 1, 1), ctx=None):
        super(Scene, self).__init__(size, background, ctx)

        self._camera = (
            Matrix44.perspective_projection(45., 1., 0.1, 1000.)
        ).astype(np.float32)
        self._camera_position = Vector3([-2., -2, -2], dtype="float32")
        self._camera_target = Vector3([0., 0, 0], dtype="float32")
        self._rotation = Matrix44.identity().astype(np.float32)
        self._up_vector = Vector3([0, 0, 1], dtype="float32")
        self._light = Vector3([-0.5, -0.8, -2], dtype="float32")

        self._uniforms = dict(
            # raw uniforms
            light=self._light,
            camera=self._camera,
            camera_position=self._camera_position,
            camera_target=self._camera_target,
            rotation=self._rotation,
            up_vector=self._up_vector,

            # derivative uniforms
            vm=self.vm,
            mv=self.mv,
            mvp=self.mvp
        )

    def _update_uniforms(self):
        self._uniforms["mvp"] = self.mvp
        self._uniforms["mv"] = self.mv
        self._uniforms["vm"] = self.vm

    @property
    def vm(self):
        return self.mv.inverse

    @property
    def mv(self):
        return (Matrix44.look_at(
            self._camera_position,
            self._camera_target,
            self._up_vector
        ) * self._rotation).astype(np.float32)

    @property
    def mvp(self):
        return (self._camera * self.mv).astype(np.float32)

    @property
    def light(self):
        return self._light.copy()

    @light.setter
    def light(self, l):
        self._light[...] = l

    @property
    def camera_matrix(self):
        return self._camera.copy()

    @camera_matrix.setter
    def camera_matrix(self, cam):
        self._camera[...] = cam
        self._update_uniforms()

    @property
    def camera_position(self):
        return self._camera_position.copy()

    @camera_position.setter
    def camera_position(self, pos):
        self._camera_position[...] = pos
        self._update_uniforms()

    @property
    def camera_target(self):
        return self._camera_target.copy()

    @camera_target.setter
    def camera_target(self, target):
        self._camera_target[...] = target
        self._update_uniforms()

    @property
    def up_vector(self):
        return self._up_vector.copy()

    @up_vector.setter
    def up_vector(self, up):
        self._up_vector[...] = up
        self._update_uniforms()

    @property
    def rotation(self):
        return self._rotation.copy()

    @rotation.setter
    def rotation(self, rot):
        self._rotation[...] = rot
        self._update_uniforms()

    def rotate_x(self, angle):
        self._rotation *= Matrix44.from_x_rotation(angle)
        self._update_uniforms()

    def rotate_y(self, angle):
        self._rotation *= Matrix44.from_y_rotation(angle)
        self._update_uniforms()

    def rotate_z(self, angle):
        self._rotation *= Matrix44.from_z_rotation(angle)
        self._update_uniforms()

    @property
    def uniforms(self):
        return list(self._uniforms.items())
