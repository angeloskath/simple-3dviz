"""Visualize mesh files. Use the `--help` argument for information on how to
use the script."""

import argparse
from functools import reduce
from os import path
from tempfile import gettempdir

import numpy as np

from .. import Mesh, Scene
from ..behaviours.keyboard import SnapshotOnKey
from ..behaviours.misc import LightToCamera
from ..utils import save_frame
try:
    from ..window import show
    no_gui = False
except ImportError:
    no_gui = True


# The tab20 colormap from matplotlib
tab20 = [
    (0.12156862745098039, 0.4666666666666667,  0.7058823529411765  ),
    (0.6823529411764706,  0.7803921568627451,  0.9098039215686274  ),
    (1.0,                 0.4980392156862745,  0.054901960784313725),
    (1.0,                 0.7333333333333333,  0.47058823529411764 ),
    (0.17254901960784313, 0.6274509803921569,  0.17254901960784313 ),
    (0.596078431372549,   0.8745098039215686,  0.5411764705882353  ),
    (0.8392156862745098,  0.15294117647058825, 0.1568627450980392  ),
    (1.0,                 0.596078431372549,   0.5882352941176471  ),
    (0.5803921568627451,  0.403921568627451,   0.7411764705882353  ),
    (0.7725490196078432,  0.6901960784313725,  0.8352941176470589  ),
    (0.5490196078431373,  0.33725490196078434, 0.29411764705882354 ),
    (0.7686274509803922,  0.611764705882353,   0.5803921568627451  ),
    (0.8901960784313725,  0.4666666666666667,  0.7607843137254902  ),
    (0.9686274509803922,  0.7137254901960784,  0.8235294117647058  ),
    (0.4980392156862745,  0.4980392156862745,  0.4980392156862745  ),
    (0.7803921568627451,  0.7803921568627451,  0.7803921568627451  ),
    (0.7372549019607844,  0.7411764705882353,  0.13333333333333333 ),
    (0.8588235294117647,  0.8588235294117647,  0.5529411764705883  ),
    (0.09019607843137255, 0.7450980392156863,  0.8117647058823529  ),
    (0.6196078431372549,  0.8549019607843137,  0.8980392156862745  )
]


def list_of(f):
    def inner(x):
        try:
            return [f(xi) for xi in x.split(";")]
        except ValueError as e:
            raise ValueError("Error when parsing the list of elements") from e
    return inner

def or_type(f1, f2):
    def inner(x):
        try:
            return f1(x)
        except ValueError:
            return f2(x)
    return inner


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
        default="The mesh to be viewed",
        nargs="+"
    )
    parser.add_argument(
        "--size",
        type=int_tuple(2),
        default=(512, 512),
        help="The size of the window"
    )
    parser.add_argument(
        "--background", "-b",
        type=or_type(f_tuple(4), f_tuple(3)),
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
        type=list_of(or_type(f_tuple(4), f_tuple(3))),
        default=[(0.3, 0.3, 0.3)],
        help="Choose a color for the mesh"
    )
    parser.add_argument(
        "--use_tab20",
        action="store_true",
        help="Use matplotlib's tab20 color map"
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
    parser.add_argument(
        "--direct_render",
        help="If provided render to this file and exit"
    )

    args = parser.parse_args(argv)

    colors = args.color*len(args.file) if len(args.color) == 1 else args.color
    if args.use_tab20:
        colors = [tab20[i % 20] for i in range(len(args.file))]
    meshes = [
        Mesh.from_file(f, color=c)
        for f, c in zip(args.file, colors)
    ]

    if args.auto:
        bbox_min = reduce(
            np.minimum,
            (m.bbox[0] for m in meshes),
            meshes[0].bbox[0]
        )
        bbox_max = reduce(
            np.maximum,
            (m.bbox[1] for m in meshes),
            meshes[0].bbox[1]
        )
        bbox = [bbox_min, bbox_max]
        center = (bbox[1]-bbox[0])/2 + bbox[0]
        args.camera_target = center
        args.camera_position = center + (bbox[1]-center)*2
        D = np.sqrt(np.sum((args.camera_position - args.camera_target)**2))
        if D > 100:
            s = 100. / D
            args.camera_target *= s
            args.camera_position *= s
            for m in meshes:
                m.scale(s)

    behaviours = [
        SnapshotOnKey(path=args.save_frame, keys={"<ctrl>", "S"}),
    ]
    if args.light is None:
        behaviours.append(LightToCamera())

    if args.direct_render:
        scene = Scene(size=args.size, background=args.background)
        for m in meshes:
            m.sort_triangles(args.camera_position)
            scene.add(m)
        scene.camera_position = args.camera_position
        scene.camera_target = args.camera_target
        scene.up_vector = args.up
        if args.light is None:
            scene.light = args.camera_position
        else:
            scene.light = args.light
        scene.render()
        save_frame(args.direct_render, scene.frame)
    else:
        show(
            meshes,
            size=args.size, background=args.background, title="Mesh Viewer",
            camera_position=args.camera_position,
            camera_target=args.camera_target,
            up_vector=args.up,
            light=args.light,
            behaviours=behaviours
        )
