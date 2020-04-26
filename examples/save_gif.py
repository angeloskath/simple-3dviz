
import numpy as np
from simple_3dviz import Spherecloud, render
from simple_3dviz.behaviours.io import SaveGif
from simple_3dviz.behaviours.movements import RotateModel


if __name__ == "__main__":
    # Make a random point cloud
    centers = np.random.randn(30, 3)
    colors = np.array([[1., 0, 0, 1],
                       [0, 1, 1, 1]])[np.random.randint(0, 2, size=30)]
    sizes = np.ones(30)*0.2

    # render it and save the animation as a gif
    render(
        Spherecloud(centers, colors, sizes),
        [RotateModel(), SaveGif("/tmp/spheres.gif")],
        180,
        camera_position=(3, 3, 3),
        background=(0,)*4
    )

