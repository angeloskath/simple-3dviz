
import unittest

from cv2 import imwrite
import numpy as np

from simple_3dviz import Scene, Lines, Spherecloud
from simple_3dviz.window import show


class TestLines(unittest.TestCase):
    def test_line(self):
        points = np.array([[-0.5, 0.5, -0.5],
                           [ 0.5,  0.5,  0.5]])
        colors = np.array([[0., 0., 0., 1.],
                           [0., 0., 0., 1.]])

        show(Lines(points, colors, width=0.1))


if __name__ == "__main__":
    unittest.main()
