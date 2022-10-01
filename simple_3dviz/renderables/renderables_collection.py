from os import path
from collections import defaultdict

import numpy as np

from ..io import read_material_file
from ..io._utils import get_file, close_file
from .mesh import MeshBase
from .textured_mesh import Material, TexturedMesh


class RenderablesCollectionReader:
    def __init__(self, renderables_params):
        self.renderables_params = renderables_params

    def to_renderables(self):
        renderables = [
            TexturedMesh.from_params(rp)
            for rp in self.renderables_params
        ]
        return renderables

    @staticmethod
    def unpack_face(face, vertices, normals, uv):
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

    @classmethod
    def from_file(cls, filepath, material_filepath, ext=None,
                  material_ext=None, color=(0.5, 0.5, 0.5)):
        """Read the meshes from a file.

        Arguments
        ---------
            filepath: Path to file or file object containing the mesh
            material_filepath: Path to file containing the material
            ext: The file extension (including the dot) if 'filepath' is an
                 object
            material_ext: The file extension (including the dot) if 'filepath'
                          is an object
            color: A color to use if the material is neither given nor found
        """
        # Read the material_filepath and extract the info for all materials
        materials = read_material_file(
            material_filepath, ext=material_ext
        )._materials

        # Parse
        f = get_file(filepath)

        lines = f.readlines()
        # Collect all the vertices, namely lines starting with 'v' followed
        # by 3 floats and arrange them according to faces
        vertices_all = np.array([
            list(map(float, l.strip().split()[1:4]))
            for l in lines if l.startswith("v ")
        ], dtype=np.float32)
        # Collect all the vertex normals, namely lines starting with 'vn'
        # followed by 3 floats and arrange the according to faces
        try:
            normals_all = np.array([
                list(map(float, l.strip().split()[1:]))
                for l in lines if l.startswith("vn ")
            ])
        except IndexError:
            pass

        # Collect all the texture coordinates, namely u, v [,w] coordinates
        try:
            uv_all = np.array([
                list(map(float, l.strip().split()[1:]))
                for l in lines if l.startswith("vt ")
            ])
        except IndexError:
            pass


        material = None
        vertices = defaultdict(list)
        normals = defaultdict(list)
        uv = defaultdict(list)
        for line in lines:
            if line.startswith("usemtl "):
                material = line.strip().split()[-1]

            if line.startswith("f "):
                fv, fn, fu = cls.unpack_face(
                    line.split()[1:], vertices_all, normals_all, uv_all
                )
                if fv is not None:
                    vertices[material].extend(fv)
                if fn is not None:
                    normals[material].extend(fn)
                if fu is not None:
                    uv[material].extend(fu)

        rparams = []
        for k in vertices.keys():
            material = None
            if k in materials:
                material = Material(
                    ambient=materials[k]["ambient"],
                    diffuse=materials[k]["diffuse"],
                    specular=materials[k]["specular"],
                    Ns=materials[k]["Ns"],
                    texture=materials[k]["texture"],
                    bump_map=materials[k]["bump"]
                )
            rparams.append({
                "vertices": np.asarray(vertices[k]),
                "normals": np.asarray(normals[k]) if len(normals[k]) > 0 else None,
                "uv": np.asarray(uv[k]) if len(uv[k]) > 0 else None,
                "material": material
            })

        close_file(filepath, f)

        return cls(rparams)
