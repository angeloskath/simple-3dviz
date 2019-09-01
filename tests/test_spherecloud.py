
import unittest

from cv2 import imwrite
import numpy as np

from simple_3dviz import Scene, Spherecloud

class TestSpherecloud(unittest.TestCase):
    def test_spherecloud(self):
        centers = np.random.randn(5000, 3)
        colors = np.ones((5000, 4))*[0.8, 0.1, 0.8, 1.0]
        sizes = np.random.rand(5000)*0.02 + 0.01

        s = Scene(size=(1024, 1024), background=(1,)*4)
        s.add(Spherecloud(centers, colors, sizes))
        s.camera_position = (-10, -10, -10)
        for i in range(180):
            s.render()
            imwrite("/tmp/frame_{:03d}.png".format(i), s.frame)
            s.rotate_z(np.pi/90)


if __name__ == "__main__":
    unittest.main()
