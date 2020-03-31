import numpy as np

from simple_3dviz import Spherecloud
from simple_3dviz.renderables import Mesh
from simple_3dviz.behaviours.movements import CameraTrajectory
from simple_3dviz.behaviours.misc import LightToCamera
from simple_3dviz.behaviours.io import SaveFrames
from simple_3dviz.behaviours.trajectory import Circle
from simple_3dviz.window import show
from simple_3dviz.utils import render


if __name__ == "__main__":
    # Sample code for replicating the example from
    # https://matplotlib.org/3.2.1/gallery/mplot3d/voxels.html

    # Prepare some coordinates
    x, y, z = np.indices((8, 8, 8))
    
    # Draw cuboids in the top left and bottom right corners, and a link between
    # them
    cube1 = (x < 3) & (y < 3) & (z < 3)
    cube2 = (x >= 5) & (y >= 5) & (z >= 5)
    link = abs(x - y) + abs(y - z) + abs(z - x) <= 2
    
    # Combine the objects into a single boolean array
    voxels = cube1 | cube2 | link
    
    # Set the colors of each object
    colors = np.empty(voxels.shape + (3,), dtype=np.float32)
    colors[link] = (1, 0, 0)
    colors[cube1] = (0, 0, 1)
    colors[cube2] = (0, 1, 0)

    show(
        Mesh.from_voxel_grid(voxels=voxels, colors=colors),
        light=(-1, -1, 1),
        behaviours=[
            CameraTrajectory(
                Circle(center=(0, 0, 0), point=(2, -1, 0), normal=(0, 0, -1)),
                speed=0.004)
        ]
    )

    # Render scene to file
    # render(
    #     Mesh.from_voxel_grid(voxels=voxels, colors=colors),
    #     n_frames=256,
    #     light=(-1, -1, 1),
    #     behaviours=[
    #         CameraTrajectory(
    #             Circle(center=(0, 0, 0), point=(2, -1, 0), normal=(0, 0, -1)),
    #             speed=0.004
    #         ),
    #         SaveFrames("/tmp/frame_{:03d}.png", every_n=3)
    #     ],
    #     size=(256, 256)
    # )

    # Make a random point cloud
    x = np.linspace(-0.7, 0.7, num=10)
    centers = np.array(np.meshgrid(x, x, x)).reshape(3, -1).T
    spheres_colors = np.array([[1, 1, 0, 1],
                       [0, 1, 1, 1]])[np.random.randint(0, 2, size=centers.shape[0])]
    spheres_sizes = np.ones(centers.shape[0])*0.02

    show(
        [
            Mesh.from_voxel_grid(voxels=voxels, colors=colors),
            Spherecloud(
                centers=centers, colors=spheres_colors, sizes=spheres_sizes
            )
        ],
        light=(-1, -1, 1),
        behaviours=[
            CameraTrajectory(
                Circle(center=(0, 0, 0), point=(2, -2, 0), normal=(0, 0, -1)),
                speed=0.004)
        ]
    )
    #render(
    #    [
    #        Mesh.from_voxel_grid(voxels=voxels, colors=colors),
    #        Spherecloud(
    #            centers=centers, colors=spheres_colors, sizes=spheres_sizes
    #        )
    #    ],
    #    n_frames=256,
    #    behaviours=[
    #        CameraTrajectory(
    #            Circle(center=(0, 0, 0), point=(2, -2, 0), normal=(0, 0, -1)),
    #            speed=0.004
    #        ),
    #        LightToCamera(),
    #        SaveFrames("/tmp/frame_{:03d}.png", every_n=3)
    #    ],
    #    size=(256,256)
    #)

