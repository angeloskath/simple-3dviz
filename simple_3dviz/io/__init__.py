"""Provide a common interface for loading mesh files or other useful files."""

from os import path

from .mesh import ObjMeshReader, OffMeshReader, PlyMeshReader, StlMeshReader


def read_mesh_file(filename):
    _, ext = path.splitext(filename)
    try:
        return {
            ".ply": PlyMeshReader,
            ".obj": ObjMeshReader,
            ".off": OffMeshReader,
            ".stl": StlMeshReader
        }[ext](filename)
    except KeyError as e:
        raise ValueError("{} mesh file extension is not supported".format(ext))
