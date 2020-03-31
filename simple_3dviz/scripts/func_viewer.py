"""Visualize two-dimensional functions. Use the `--help` argument for
information on how to use the script."""

import argparse

import matplotlib.pyplot as plt
import numpy as np

from .. import Mesh, Lines
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


def get_colormap(cmap, log_colors):
    cmap = plt.cm.get_cmap(cmap)
    def normalize(x):
        xmin = x.min()
        xmax = x.max()
        return (x-xmin)/(xmax-xmin)

    def colors(x):
        if log_colors:
            return cmap(normalize(np.log(np.maximum(x, 1e-7))))
        else:
            return cmap(normalize(x))

    return colors


def get_function(func, xlim, ylim, n, cmap="viridis", log_colors=False):
    x = np.linspace(xlim[0], xlim[1], n)
    y = np.linspace(ylim[0], ylim[1], n)
    X, Y = np.meshgrid(x, y)
    Z = eval(func, dict(x=X, y=Y, np=np))

    return Mesh.from_xyz(X, Y, Z, colormap=get_colormap(cmap, log_colors))


def get_axes():
    return Lines(
        [[-1, -1, -1],
         [ 1, -1, -1],
         [-1, -1, -1],
         [-1,  1, -1],
         [-1, -1, -1],
         [-1, -1,  1]],
        [[0.5, 0.5, 0.5, 1.],
         [0.5, 0.5, 0.5, 1.],
         [0.5, 0.5, 0.5, 1.],
         [0.5, 0.5, 0.5, 1.],
         [0.5, 0.5, 0.5, 1.],
         [0.5, 0.5, 0.5, 1.]],
        width=0.01
    )


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Visualize functions with simple_3dviz"
    )
    parser.add_argument(
        "function",
        default="The function to be viewed as a python string (use x, y and np)"
    )
    parser.add_argument(
        "--n_points",
        type=int,
        default=100,
        help="How many points per dimension"
    )
    parser.add_argument(
        "--xlim",
        type=f_tuple(2),
        default=(-1., 1.),
        help="The limits for the x axis"
    )
    parser.add_argument(
        "--ylim",
        type=f_tuple(2),
        default=(-1., 1.),
        help="The limits for the y axis"
    )
    parser.add_argument(
        "--colormap",
        default="jet",
        help="Set the matplotlib colormap"
    )
    parser.add_argument(
        "--log_colors",
        action="store_true",
        help="Use logspace for assigning the colors"
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
        default=(3, 3, 3),
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
        "--no_axes",
        action="store_false",
        dest="axes",
        help="Do not show the axes"
    )

    args = parser.parse_args(argv)

    mesh = get_function(args.function, args.xlim, args.ylim,
                        args.n_points, args.colormap, args.log_colors)
    axes = get_axes()
    show(
        [mesh] + ([axes] if args.axes else []),
        size=args.size, background=args.background, title="Func Viewer",
        camera_position=args.camera_position, camera_target=args.camera_target,
        up_vector=args.up, light=args.light
    )
