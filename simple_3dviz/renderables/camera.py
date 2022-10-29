"""A renderable to add a camera object as well as rays and rendered images."""

from importlib.resources import open_text

import numpy as np
from pyrr import Matrix44

from .base import Renderable
from .mesh import Mesh

def _normalize(x):
    return x / np.sqrt((x**2).sum())


class Camera(Renderable):
    """"""

    def __init__(self, camera_size, camera_position, camera_target, up_vector, right_vector):
        self.camera = Mesh.from_file(
            open_text("simple_3dviz.data_files", "camera.obj"),
            ext=".obj"
        )
        self._place_camera(camera_size, camera_position, camera_target, up_vector, right_vector)

    def _place_camera(self, camera_size, camera_position, camera_target, up_vector, right_vector):
        camera_size, camera_position, camera_target, up_vector, right_vector = map(
            np.asarray,
            (camera_size, camera_position, camera_target, up_vector, right_vector)
        )
        self.camera.to_unit_cube()
        t = camera_position
        S = np.eye(3) * camera_size
        R = Matrix44.look_at(camera_position, camera_target, up_vector).T[:3, :3]
        R = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0.]]) @ R

        self.camera.affine_transform(S @ R, t)

    def init(self, ctx):
        self.camera.init(ctx)

    def release(self):
        self.camera.release()

    def update_uniforms(self, uniforms):
        self.camera.update_uniforms(uniforms)

    def render(self):
        self.camera.render()

    def scale(self, s):
        self.camera.scale(s)
    
    def affine_transform(self, R=np.eye(3), t=np.zeros(3)):
        self.camera.affine_transform(R, t)
