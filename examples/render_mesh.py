import numpy as np
import matplotlib.pyplot as plt

from simple_3dviz.renderables import Mesh
from simple_3dviz.behaviours.keyboard import SnapshotOnKey
from simple_3dviz.window import show


if __name__ == "__main__":
    dphi, dtheta = np.pi/250.0, np.pi/250.0
    [phi, theta] = np.mgrid[0:np.pi+dphi*1.5:dphi, 0:2*np.pi+dtheta*1.5:dtheta]
    m0 = 4; m1 = 3; m2 = 2; m3 = 3; m4 = 6; m5 = 2; m6 = 6; m7 = 4;
    r = np.sin(m0 * phi)**m1 + np.cos(m2 * phi)**m3
    r = r + np.sin(m4 * theta)**m5 + np.cos(m6 * theta)**m7
    x = r * np.sin(phi) * np.cos(theta)
    y = r * np.cos(phi)
    z = r * np.sin(phi) * np.sin(theta)
    m = Mesh.from_xyz(x, y, z)
    show(
        m,
        camera_position=(0, 2.32, 2.47),
        up_vector=( -0.7265758,-0.35081482,0.12523057),
        behaviours=[SnapshotOnKey()],
        size=(256,256)
    )

    # It is also possible to load a mesh with a colormap
    m = Mesh.from_xyz(x, y, z, colormap=plt.cm.jet)
    show(
        m,
        camera_position=(0, 2.32, 2.47),
        up_vector=( -0.7265758,-0.35081482,0.12523057),
        behaviours=[SnapshotOnKey()],
        size=(256,256)
    )
