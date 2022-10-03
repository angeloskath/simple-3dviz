
from simple_3dviz.behaviours.io import SaveGif
from simple_3dviz.behaviours.movements import CameraTrajectory
from simple_3dviz.behaviours.trajectory import Circle
from simple_3dviz.renderables import TexturedMesh
from simple_3dviz.utils import render
from simple_3dviz.window import show


if __name__ == "__main__":

    # The 3D model together with its material is from ShapeNet
    rr1 = TexturedMesh.from_file("/tmp/motorbikes/45009f5fa4cb295e52ee90e577613070/model.obj")
    rr1.to_unit_cube()
    show(
        rr1,
        up_vector=(0, 1, 0),
        size=(1200, 1200),
        camera_position=(0.0, 0.6, 1.4),
        light=(0,5,0)
    )
    # Render the scene and save the animation as a gif
    render(
        rr1,
        [
            CameraTrajectory(
                Circle((0, 0, 0), (0.0, 0.60, 1.4), (0, -1, 0)),
                speed=1/180
            ),
            SaveGif("/tmp/motorbike_1.gif")
        ],
        180,
        camera_position=(0.0, 0.60, 1.4),
        light=(0,)*3,
        background=(1.0,)*4,
        up_vector=(0, 1, 0)
    )

    # The 3D model together with its material is from ShapeNet
    rr2 = TexturedMesh.from_file("/tmp/motorbikes/46e38cf88b07de0ee2b85785c47c5d52/model.obj")
    show(
        rr2,
        up_vector=(0, 1, 0),
        size=(1200, 1200),
        camera_position=(0.0, 0.40, 1.0),
        light=(0,0,0)
    )

    # Render the scene and save the animation as a gif
    render(
        rr2,
        [
            CameraTrajectory(
                Circle((0, 0, 0), (0.0, 0.40, 1.0), (0, -1, 0)),
                speed=1/180
            ),
            SaveGif("/tmp/motorbike_2.gif")
        ],
        180,
        camera_position=(0.0, 0.40, 1.0),
        light=(0,)*3,
        background=(1.0,)*4,
        up_vector=(0, 1, 0)
    )

    # It is possible to turn off the culling of faces that are pointing away
    # from the camera, which by default is set to true
    if hasattr(rr2, "renderables"):
        for r in rr2.renderables:
            r.cull_back_face = False
        else:
            rr2.cull_back_face = False
    # Render the scene and save the animation as a gif
    render(
        rr2,
        [
            CameraTrajectory(
                Circle((0, 0, 0), (0.0, 0.40, 1.0), (0, -1, 0)),
                speed=1/180
            ),
            SaveGif("/tmp/motorbike_3.gif")
        ],
        180,
        camera_position=(0.0, 0.40, 1.0),
        light=(0,)*3,
        background=(1.0,)*4,
        up_vector=(0, 1, 0)
    )
