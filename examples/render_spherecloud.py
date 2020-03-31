import numpy as np
import matplotlib.pyplot as plt

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
    cmap = plt.cm.copper
    colors = cmap(np.random.choice(np.arange(500), centers.shape[0]))
    s = Spherecloud(centers=centers, sizes=sizes, colors=colors)

    from simple_3dviz import Mesh
    m = Mesh.from_file("models/baby_yoda.stl", color=(0.1, 0.8, 0.1))
    m.to_unit_cube()
    show([s, m], camera_position=(-2.8, -2.8, 0.1), size=(512, 512))
