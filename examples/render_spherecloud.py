import numpy as np

from simple_3dviz.renderables import Spherecloud
from simple_3dviz.behaviours.keyboard import SnapshotOnKey
from simple_3dviz.window import show


if __name__ == "__main__":
    t = np.linspace(0, 4 * np.pi, 20)
    x = np.sin(2 * t)
    y = np.cos(t)
    z = np.cos(2 * t)
    sizes = (2 + np.sin(t)) * 0.125
    centers = np.stack([x, y, z]).reshape(3, -1).T
    print(sizes)
    s = Spherecloud(centers=centers, sizes=sizes))
    show(s)
