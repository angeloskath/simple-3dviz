"""Visualize mesh files. Use the `--help` argument for information on how to
use the script."""

import argparse
from os import path
from tempfile import gettempdir

import numpy as np

from .. import Mesh
from ..behaviours.keyboard import SnapshotOnKey
from ..behaviours.misc import LightToCamera
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
        default=None
    )
    parser.add_argument(
        "--color",
        type=f_tuple(3),
        default=(0.3, 0.3, 0.3),
        help="Choose a color for the mesh"
    )
    parser.add_argument(
        "--manual",
        action="store_false",
        dest="auto",
        help="Auto determine the camera position and target"
    )
    parser.add_argument(
        "--save_frame",
        default=path.join(gettempdir(), "frame_{:03d}.png"),
        help="The location to save the snapshot frame"
    )

    args = parser.parse_args(argv)

    mesh = Mesh.from_file(args.file, color=args.color)

    if args.auto:
        bbox = mesh.bbox
        center = (bbox[1]-bbox[0])/2 + bbox[0]
        args.camera_target = center
        args.camera_position = center + (bbox[1]-center)*2
        D = np.sqrt(np.sum((args.camera_position - args.camera_target)**2))
        if D > 100:
            s = 100. / D
            args.camera_target *= s
            args.camera_position *= s
            mesh.scale(s)

    behaviours = [
        SnapshotOnKey(path=args.save_frame, keys={"<ctrl>", "S"})
    ]
    if args.light is None:
        behaviours.append(LightToCamera())

    show(
        mesh,
        size=args.size, background=args.background, title="Mesh Viewer",
        camera_position=args.camera_position, camera_target=args.camera_target,
        up_vector=args.up, light=args.light,
        behaviours=behaviours
    )
