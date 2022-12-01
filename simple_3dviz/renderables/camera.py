"""A renderable to add a camera object as well as rays and rendered images."""

from importlib.resources import open_text

import numpy as np
from pyrr import Matrix44

from ..utils import read_image
from .base import Renderable
from .mesh import Mesh
from .lines import Lines
from .image import Image
from .spherecloud import Spherecloud

def _normalize(x):
    return x / np.sqrt((x**2).sum())


class Camera(Renderable):
    """"""

    def __init__(self, K, R_world_to_cam, translation, camera_size):
        self.camera = Mesh.from_file(
            open_text("simple_3dviz.data_files", "camera.obj"),
            ext=".obj"
        )
        self.K = K
        self.R_world_to_cam = R_world_to_cam
        self.translation = translation
        self.camera_size = camera_size
        self._place_camera()

        self._ctx = None
        self.rays = None
        self.image = None
        self.points = None

    def _place_camera(self):
        self.camera.to_unit_cube()
        S = np.eye(3) * self.camera_size

        t = self.translation
        R = self.R_world_to_cam
        # Permute the dimensions to account for the way the camera mesh was
        # designed
        R = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0.]]) @ R

        self.camera.affine_transform(S @ R, t)

    def _ray_direction_from_pixel(self, u, v):
        fx, fy = self.K[0][0], self.K[1][1]
        ox, oy = self.K[0][2], self.K[1][2]
        pts_screen = np.array([[
            (u - ox) / fx,
            -(v - oy) / fy,  # - yc in order for the direction of y to be upwards
            -1
        ]]).T
        direction = self.R_world_to_cam.T @ pts_screen

        return direction.ravel()

    def add_ray(self, u, v, start=0.0, stop=1.0, color=(0.3, 0.3, 0.3)):
        direction = self._ray_direction_from_pixel(u, v)
        a = start * direction + self.translation
        b = stop * direction + self.translation
        if self.rays is None:
            self.rays = Lines([a, b], color, width=0.005)
            if self._ctx is not None:
                self.rays.init(self._ctx)
        else:
            self.rays.append([a, b], color)

    def add_ray_points(
        self, u, v, start=0.3, stop=3.7, num_points=32, color=(0.3, 0.3, 0.3)
    ):
        direction = self._ray_direction_from_pixel(u, v)
        z_vals = np.linspace(start, stop, num=num_points)
        z_vals = z_vals + np.random.rand(num_points) * (stop - start) / num_points
        points = np.repeat(self.translation[:, None], len(z_vals), axis=1)
        points = points + direction[:, None] * z_vals[None, :]
        points = points.T
        if self.points is None:
            self.points = Spherecloud(points, colors=color, sizes=0.01)
            if self._ctx is not None:
                self.points.init(self._ctx)
        else:
            self.points.append(points, colors=color, sizes=0.01)

    def add_image(self, image, depth=1.0):
        if self.image is not None:
            self.image.release()

        if isinstance(image, str):
            image = read_image(image)
        H, W = image.shape[:2]
        image = image[:, ::-1]

        n = self._ray_direction_from_pixel(W/2, H/2)
        d1 = self._ray_direction_from_pixel(0, 0)
        d2 = self._ray_direction_from_pixel(W-1, 0)
        position = self.translation + depth * n
        width = depth*np.sqrt(((d2 - d1)**2).sum())

        self.image = Image(
            image,
            position=position,
            normal=n,
            right_vector=d1-d2,
            size=(width, None),
        )
        self.image.opacity = 0.5

        if self._ctx is not None:
            self.image.init(ctx)

    def init(self, ctx):
        self._ctx = ctx
        self.camera.init(ctx)
        if self.rays is not None:
            self.rays.init(ctx)
        if self.image is not None:
            self.image.init(ctx)
        if self.points is not None:
            self.points.init(ctx)

    def release(self):
        self.camera.release()
        if self.rays is not None:
            self.rays.release()
        if self.image is not None:
            self.image.release()
        if self.points is not None:
            self.points.release()

    def update_uniforms(self, uniforms):
        self.camera.update_uniforms(uniforms)
        if self.rays is not None:
            self.rays.update_uniforms(uniforms)
        if self.image is not None:
            self.image.update_uniforms(uniforms)
        if self.points is not None:
            self.points.update_uniforms(uniforms)

    def render(self):
        self.camera.render()
        if self.rays is not None:
            self.rays.render()
        if self.image is not None:
            self.image.render()
        if self.points is not None:
            self.points.render()

    def scale(self, s):
        raise NotImplementedError()
    
    def affine_transform(self, R=np.eye(3), t=np.zeros(3)):
        raise NotImplementedError()
