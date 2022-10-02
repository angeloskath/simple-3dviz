"""Provide a common interface for loading mesh files or other useful files."""

from os import path

from .material import MtlMaterialReader
from .mesh import ObjMeshReader, OffMeshReader, PlyMeshReader, StlMeshReader


def read_mesh_file(filename, ext=None):
    if isinstance(filename, str):
        _, ext = path.splitext(filename)
    try:
        return {
            ".ply": PlyMeshReader,
            ".obj": ObjMeshReader,
            ".off": OffMeshReader,
            ".stl": StlMeshReader
        }[ext.lower()](filename)
    except KeyError as e:
        raise ValueError("{} mesh file extension is not supported".format(ext))


def read_material_file(filename, ext=None):
    if isinstance(filename, str):
        _, ext = path.splitext(filename)
    try:
        return {
            ".mtl": MtlMaterialReader
        }[ext.lower()](filename)
    except KeyError as e:
        raise ValueError("{} material file extension is not supported".format(ext))


