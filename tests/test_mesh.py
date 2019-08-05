
import unittest

import numpy as np
from pyrr import Matrix44
from scipy.spatial import ConvexHull
from skimage.io import imsave

from simple_3dviz import Scene, Mesh

class TestMesh(unittest.TestCase):
    def test_mesh(self):
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

        perspective = Matrix44.perspective_projection(45.0, 1.0, 0.1, 1000.0)
        lookat = Matrix44.look_at(
            ( -2,  -2,  -2),
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 1.0),
        )
        mvp = perspective * lookat

        s = Scene(size=(1024, 1024), background=(0, 0, 0, 0))
        s._uniforms["light"][...] = [-0.5, 0.5, -2]
        s._uniforms["mvp"][...] = mvp
        s.add(Mesh(vertices, normals, colors))

        for i in range(360):
            s._uniforms["mvp"][...] = mvp * Matrix44.from_z_rotation(i*np.pi/180)
            s.render()
            imsave("/tmp/frame_{:03d}.png".format(i), s.frame)


if __name__ == "__main__":
    unittest.main()

