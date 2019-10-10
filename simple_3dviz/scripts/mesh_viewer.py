
import argparse
from os import path
from tempfile import gettempdir

from .. import Mesh
from ..behaviours.keyboard import SnapshotOnKey
from ..window import show


def int_tuple(n):
    def inner(x):
        t = tuple(int(xi) for xi in x.split(","))
        if len(t) != n:
            raise ValueError("Expected a {}-tuple".format(n))
        return t
    return inner


def f_tuple(n):
    def inner(x):
        t = tuple(float(xi) for xi in x.split(","))
        if len(t) != n:
            raise ValueError("Expected a {}-tuple".format(n))
        return t
    return inner


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Visualize meshes with simple_3dviz"
    )
    parser.add_argument(
        "file",
        default="The mesh to be viewed"
    )
    parser.add_argument(
        "--size",
        type=int_tuple(2),
        default=(512, 512),
        help="The size of the window"
    )
    parser.add_argument(
        "--background", "-b",
        type=f_tuple(4),
        default=(0.7, 0.7, 0.7, 1),
        help="The rgba background color"
    )
    parser.add_argument(
        "--camera_position", "-c",
        type=f_tuple(3),
        default=(-2, -2, -2),
        help="The position of the camera"
    )
    parser.add_argument(
        "--camera_target", "-t",
        type=f_tuple(3),
        default=(0, 0, 0),
        help="The target of the camera"
    )
    parser.add_argument(
        "--up",
        type=f_tuple(3),
        default=(0, 0, 1),
        help="The up vector"
    )
    parser.add_argument(
        "--light",
        type=f_tuple(3),
        default=(-0.5, -0.8, -2)
    )
    parser.add_argument(
        "--save_frame",
        default=path.join(gettempdir(), "frame_{:03d}.png"),
        help="The location to save the snapshot frame"
    )

    args = parser.parse_args(argv)

    show(
        Mesh.from_file(args.file),
        size=args.size, background=args.background, title="Mesh Viewer",
        camera_position=args.camera_position, camera_target=args.camera_target,
        up_vector=args.up, light=args.light,
        behaviours=[SnapshotOnKey(path=args.save_frame, keys={"<ctrl>", "S"})]
    )
