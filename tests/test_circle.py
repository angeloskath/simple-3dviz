
import unittest

import numpy as np

from simple_3dviz import Scene, Circle

class TestCircle(unittest.TestCase):
    def test_circle(self):
        s = Scene(size=(1024, 1024))
        s.add(Circle((0.2, 0.8), 0.5, (0.1, 0.5, 0.8)))
        s.add(Circle((-0.2, 0.1), 0.2, (0.8, 0.1, 0.8)))
        s.render()

        frame = s.frame
        np.save("/tmp/frame.npy", frame)


if __name__ == "__main__":
    unittest.main()
