
from os import path
import unittest

from cv2 import imwrite
import numpy as np
from scipy.spatial import ConvexHull
import trimesh

from simple_3dviz import Scene, Mesh

class TestMesh(unittest.TestCase):
    def test_cube(self):
        points = np.array([[ 1,  1,  1],
                           [ 1,  1, -1],
                           [ 1, -1,  1],
                           [ 1, -1, -1],
                           [-1,  1,  1],
                           [-1,  1, -1],
                           [-1, -1,  1],
                           [-1, -1, -1]]) * 0.5
        hull = ConvexHull(points)
        vertices = points[hull.simplices.ravel()].reshape(-1, 3)
        normals = (np.ones((1, 3, 1)) * hull.equations[:, np.newaxis, :3]).reshape(-1, 3)
        colors = np.ones((len(vertices), 3))*[0.1, 0.5, 0.8]

        s = Scene(size=(1024, 1024), background=(0, 0, 0, 0))
        s.add(Mesh(vertices, normals, colors))

        for i in range(180):
            s.render()
            imwrite("/tmp/frame_{:03d}.png".format(i), s.frame)
            s.rotate_z(np.pi/90)
            s.rotate_x(np.pi/180)
            s.rotate_y(np.pi/360)
            s.camera_position = s.camera_position - 0.01

    def test_obj(self):
        s = Scene(size=(1024, 1024), background=(0, 0, 0, 0))
        s.add(Mesh.from_file(path.join(path.dirname(__file__), "plane.obj")))
        s.rotate_x(np.pi/2)
        s.camera_position = (-1, -1, -1)
        for i in range(180):
            s.render()
            imwrite("/tmp/frame_{:03d}.png".format(i), s.frame)
            s.rotate_y(np.pi/90)

    def test_ply(self):
        s = Scene(size=(1024, 1024), background=(0, 0, 0, 0))
        s.add(Mesh.from_file(path.join(path.dirname(__file__), "primitives.ply")))
        s.up_vector = (0, -1, 0)
        s.camera_position = (1, 0.5, 1)
        light_initial = s.light
        r_light = np.sqrt(light_initial[0]**2 + light_initial[-1]**2)
        for i in range(180):
            theta = i*np.pi/90
            r = np.sqrt(2)
            s.camera_position = (r*np.cos(theta), 0.5, r*np.sin(theta))
            s.light = (r_light*np.cos(theta), light_initial[1], r_light*np.sin(theta))
            s.render()
            imwrite("/tmp/frame_{:03d}.png".format(i), s.frame)


if __name__ == "__main__":
    unittest.main()

