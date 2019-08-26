
import unittest

import numpy as np

from simple_3dviz.behaviours.trajectory import Linear, Join, Circle, \
    QuadraticBezier


class TestTrajectories(unittest.TestCase):
    def test_linear(self):
        t = Linear(0, 1)
        for x in np.linspace(0, 1):
            self.assertEqual(x, t.get_value(x))

        t = Linear(1, 2)
        for x in np.linspace(0, 1):
            self.assertEqual(x+1, t.get_value(x))

        t = Linear(np.zeros(3), np.ones(3))
        for x in np.linspace(0, 1):
            self.assertTrue(np.all(np.ones(3)*x == t.get_value(x)))

    def test_join(self):
        t = Join([
            (0.1, Linear(0, 1)),
            (0.5, Linear(1, 0)),
            (0.1, Linear(0, -1)),
            (0.5, Linear(-1, 0))
        ])
        self.assertAlmostEqual(0, t.get_value(0))
        self.assertAlmostEqual(0.5, t.get_value(0.1/1.2/2))
        self.assertAlmostEqual(1, t.get_value(0.1/1.2))
        self.assertAlmostEqual(0.5, t.get_value(0.1/1.2 + 0.5/1.2/2))
        self.assertAlmostEqual(0, t.get_value(0.6/1.2))
        self.assertAlmostEqual(-0.5, t.get_value(0.6/1.2 + 0.1/1.2/2))
        self.assertAlmostEqual(-1, t.get_value(0.7/1.2))
        self.assertAlmostEqual(-0.5, t.get_value(0.7/1.2 + 0.5/1.2/2))
        self.assertAlmostEqual(0, t.get_value(1))

    def test_circle(self):
        t = Circle(
            [0, 0, 0],
            [1, 0, 0],
            [0, 0, 1]
        )
        self.assertTrue(np.allclose([1, 0, 0], t.get_value(0)))
        self.assertTrue(np.allclose([0, -1, 0], t.get_value(0.25)))
        self.assertTrue(np.allclose([-1, 0, 0], t.get_value(0.5)))
        self.assertTrue(np.allclose([0, 1, 0], t.get_value(0.75)))
        self.assertTrue(np.allclose([1, 0, 0], t.get_value(1.)))

        t = Circle(
            [0, 0, 0],
            [0, 1, 0],
            [-1, 0, 1]
        )
        s = np.sqrt(0.5)
        self.assertTrue(np.allclose([0, 1, 0], t.get_value(0)))
        self.assertTrue(np.allclose([s, 0, s], t.get_value(0.25)))
        self.assertTrue(np.allclose([0, -1, 0], t.get_value(0.5)))
        self.assertTrue(np.allclose([-s, 0, -s], t.get_value(0.75)))
        self.assertTrue(np.allclose([0, 1, 0], t.get_value(1.)))

        with self.assertRaises(ValueError):
            # Not a circle since radial and normal are not perpendicular
            t = Circle(
                [0, 0, 0],
                [1, 0, 0],
                [1, 1, 1]
            )

    def test_quadratic_bezier(self):
        t = QuadraticBezier(
            np.array([0., 1, 0]),
            np.array([0., 0, 0]),
            np.array([1., 0, 0])
        )
        self.assertTrue(np.allclose([0, 1, 0], t.get_value(0)))
        self.assertTrue(np.allclose([0.25, .25, 0], t.get_value(0.5)))
        self.assertTrue(np.allclose([1, 0, 0], t.get_value(1)))


if __name__ == "__main__":
    unittest.main()
