import numpy as np

from simple_3dviz import Mesh, Lines
from simple_3dviz.window import show


def heart_voxel_grid(N):
    """Create a NxNxN voxel grid with True if the voxel is inside a heart
    object and False otherwise."""
    x = np.linspace(-1.3, 1.3, N)
    y = np.linspace(-1.3, 1.3, N)
    z = np.linspace(-1.3, 1.3, N)
    x, y, z = np.meshgrid(x, y, z)
    return (2*x**2 + y**2 + z**2-1)**3 - (1/10) * x**2*z**3 - y**2*z**3 < 0


if __name__ == "__main__":
    voxels = heart_voxel_grid(64)
    m = Mesh.from_voxel_grid(voxels, colors=(0.8, 0, 0))
    l = Lines.from_voxel_grid(voxels, colors=(0, 0, 0.), width=0.001)
    show([l, m])
