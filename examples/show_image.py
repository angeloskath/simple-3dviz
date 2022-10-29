import argparse

from simple_3dviz.behaviours.misc import LightToCamera
from simple_3dviz.renderables import Image
from simple_3dviz.window import show


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Show an image in 3D space"
    )
    parser.add_argument(
        "image_path",
        help="The path to an image to show"
    )

    args = parser.parse_args()

    img = Image(args.image_path, thickness=0.02)
    show(
        img,
        camera_position=(0, -2, 0),
        behaviours=[LightToCamera()]
    )
