from collections import defaultdict
import os

import numpy as np

from ..renderables.material import Material
from . import read_material_file
from .material import MaterialReader
from .utils import get_file, close_file


class MultiMaterialObjReader:
    def __init__(self, filepath, material_filepath=None, material_ext=None,
                 color=(0.5, 0.5, 0.5)):
        self.default_material = self.make_default_material(filepath, color)
        self.materials = (
            self.read_materials(filepath, material_filepath, material_ext)
        )
        self.objects = self.read_objects(filepath)

    def make_default_material(self, filepath, color):
        # extract the filename from a possible file-like python object
        filename = filepath.name if hasattr(filepath, "name") else filepath
        texture_path = os.path.join(os.path.dirname(filename), "texture.png")
        if os.path.exists(texture_path):
            return Material.with_texture_image(texture_path, diffuse=color)
        else:
            return Material(diffuse=color)

    def read_materials(self, filepath, material_filepath, material_ext):
        try:
            # Read the material file from the obj file
            f = get_file(filepath)
            try:
                material = [
                    l.split()[1:][0] for l in f if l.startswith("mtllib")
                ][0]
                filename = f.name if hasattr(f, "name") else filepath
                material = os.path.join(os.path.dirname(filename), material)

            # or use the provided material filepath
            except IndexError:
                material = material_filepath
        finally:
            close_file(f, filepath)

        if material is not None and os.path.exists(material):
            return read_material_file(material, ext=material_ext)
        else:
            return MaterialReader()

    def read_objects(self, filepath):
        try:
            f = get_file(filepath)
            lines = f.readlines()

            # Collect all the vertices, normals and uv coordinates
            vertices_all = np.array([
                list(map(float, l.strip().split()[1:4]))
                for l in lines if l.startswith("v ")
            ], dtype=np.float32)
            normals_all = np.array([
                list(map(float, l.strip().split()[1:]))
                for l in lines if l.startswith("vn ")
            ])
            uv_all = np.array([
                list(map(float, l.strip().split()[1:]))
                for l in lines if l.startswith("vt ")
            ])

            # Gather vertices, normals and uv for each face and group them by
            # material
            material = None
            vertices = defaultdict(list)
            normals = defaultdict(list)
            uv = defaultdict(list)
            for line in lines:
                if line.startswith("usemtl "):
                    material = line.strip().split()[-1]

                if line.startswith("f "):
                    fv, fn, fu = self.unpack_face(
                        line.split()[1:], vertices_all, normals_all, uv_all
                    )
                    if fv is not None:
                        vertices[material].extend(fv)
                    if fn is not None:
                        normals[material].extend(fn)
                    if fu is not None:
                        uv[material].extend(fu)

            # Gather all the parameters to create the objects by material
            objects = []
            for k in vertices.keys():
                material = self.default_material
                if self.materials.has_material(k):
                    self.materials.set_material(k)
                    material = Material(
                        ambient=self.materials.ambient,
                        diffuse=self.materials.diffuse,
                        specular=self.materials.specular,
                        Ns=self.materials.Ns,
                        texture=self.materials.texture,
                        bump_map=self.materials.bump_map
                    )
                objects.append({
                    "vertices": np.asarray(vertices[k]),
                    "normals": np.asarray(normals[k]) if len(normals[k]) > 0 else None,
                    "uv": np.asarray(uv[k]) if len(uv[k]) > 0 else None,
                    "material": material
                })

            return objects

        finally:
            close_file(f, filepath)

    def unpack_face(self, face, vertices, normals, uv):
        def triangulate_face(face):
            triangles = []
            if len(face) == 3:
                triangles.extend(face)
            else:
                for i in range(2, len(face)):
                    triangles.extend([face[0], face[i-1], face[i]])
            return triangles

        def extract_vertex(face):
            return int(face.split("/")[0])-1

        def extract_normal(face):
            return int(face.split("/")[2])-1

        def extract_uv(face):
            return int(face.split("/")[1])-1

        faces = triangulate_face(face)
        try:
            face_vertices = np.array(list(map(extract_vertex, faces)))
            face_vertices = vertices[face_vertices].reshape(-1, 3)
        except IndexError:
            face_vertices = None

        try:
            face_normals = np.array(list(map(extract_normal, faces)))
            face_normals = normals[face_normals].reshape(-1, 3)
        except IndexError:
            face_normals = None

        try:
            face_uv = np.array(list(map(extract_uv, faces)))
            face_uv = uv[face_uv].reshape(-1, uv.shape[1])[:, :2]
        except IndexError:
            face_uv = np.zeros((len(face_vertices), 2))

        return face_vertices, face_normals, face_uv
