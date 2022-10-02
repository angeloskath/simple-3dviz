
import numpy as np
from simple_3dviz import TexturedMesh
from simple_3dviz.behaviours.movements import CameraTrajectory
from simple_3dviz.behaviours.trajectory import Circle
from simple_3dviz.renderables.textured_mesh import Material
from simple_3dviz.behaviours.misc import LightToCamera
from simple_3dviz.window import show

if __name__ == "__main__":
    tm = TexturedMesh.from_file("../models/baby_yoda.stl")
    tm.to_unit_cube()
    # show(m, behaviours=LightToCamera, size=(256,256))

    # Create various materials

    # Neon green material. When applied to an object, it will remain bright
    # green regardless of any lighting in the scene.
    m = Material(
        diffuse=(0.0, 1.0, 0.0),
        Ns=0,
        mode="constant"
    )
    r = TexturedMesh(
        tm._vertices,
        tm._normals,
        np.zeros((tm._vertices.shape[0], 2), dtype=np.float32),
        m
    )
    show(
        r,
        camera_position=(-1.3, -1.3, 0.67),
        up_vector=(0, 0, 1.0),
        behaviours=[
            CameraTrajectory(
                Circle(center=(0.0, 0.0, 0.67), point=(-1.3, -1.3, 0.67), normal=(0, 0, 1)),
                speed=0.01
            ),
            LightToCamera()
        ],
        size=(256,256)
    )

    # Flat green material
    m = Material(
        ambient=(0.0, 1.0, 0.0),
        diffuse=(0.0, 1.0, 0.0),
        Ns=0,
        mode="diffuse"
    )
    r = TexturedMesh(
        tm._vertices,
        tm._normals,
        np.zeros((tm._vertices.shape[0], 2), dtype=np.float32),
        m
    )
    show(
        r,
        camera_position=(-1.3, -1.3, 0.67),
        up_vector=(0, 0, 1.0),
        behaviours=[
            CameraTrajectory(
                Circle(center=(0.0, 0.0, 0.67), point=(-1.3, -1.3, 0.67), normal=(0, 0, 1)),
                speed=0.01
            ),
            LightToCamera()
        ],
        size=(256,256)
    )

