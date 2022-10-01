from os import path

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
    def collect_meshes(lines, lines_faces, vertices, normals, uv):

        def triangulate_faces(faces):
            triangles = []
            for f in faces:
                if len(f) == 3:
                    triangles.append(f)
                else:
                    for i in range(2, len(f)):
                        triangles.append([f[0], f[i-1], f[i]])
            return triangles

        def extract_vertex(face):
            return int(face.split("/")[0])-1

        def extract_normal(face):
            return int(face.split("/")[2])-1

        def extract_uv(face):
            return int(face.split("/")[1])-1

        faces = np.array(triangulate_faces([
            list(map(extract_vertex, l.strip().split()[1:]))
            for l in lines_faces if l.startswith("f ")
        ]))
        try:
            vertices = vertices[faces].reshape(-1, 3)
        except IndexError:
            vertices = None

        # Collect all the vertex normals, namely lines starting with 'vn'
        # followed by 3 floats and arrange the according to faces
        try:
            faces = np.array(triangulate_faces([
                list(map(extract_normal, l.strip().split()[1:]))
                for l in lines_faces if l.startswith("f ")
            ]))
            normals = normals[faces].reshape(-1, 3)
        except IndexError:
            normals = None

        # Collect all the texture coordinates, namely u, v [,w] coordinates
        try:
            faces = np.array(triangulate_faces([
                list(map(extract_uv, l.strip().split()[1:]))
                for l in lines_faces if l.startswith("f ")
            ]))
            uv = uv[faces].reshape(-1, uv.shape[1])[:, :2]
        except IndexError:
            uv = None

        return vertices, normals, uv

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
        def get_chunks_from_list(all_lines, queries):
            chunks_per_query = []
            for oi, oj in zip(queries, queries[1:]):
                oi_ii = all_lines.index(oi)
                oj_ii = all_lines.index(oj)
                chunks_per_query.append((oi.strip(), oi_ii, oj_ii-1))
            # In the end also add the indices for the last query
            chunks_per_query.append((
                queries[-1].strip(),
                all_lines.index(queries[-1]),
                len(all_lines) - 1
            ))
            return chunks_per_query
        

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

        renderables_params = []
        # Collect all the objects, namely lines starting with "o"
        objects = [l for l in lines if l.startswith("o ")]

        # Based on the object names extract the line indices that correspond to
        # each object
        chunks_per_object = get_chunks_from_list(lines, objects)

        # Now we can parse each object separately
        for object_name, start, end in chunks_per_object:
            rparams_per_object = []
            # Get the lines that correspond to this object and drop the first
            # lines that contains the object's name
            lines_per_object = lines[start : end + 1][1:]

            if len(lines_per_object) == 0:
                continue

            # For every object, we collect the materials that are associated
            # with it
            mts = [l for l in lines_per_object if l.startswith("usemtl")]
            # In case only one material is defined for this object
            if len(mts) == 1:
                start_idx = lines_per_object.index(mts[0])
                faces_lines = lines_per_object[start_idx + 1:]
                vertices, normals, uv = cls.collect_meshes(
                    lines_per_object, faces_lines,
                    vertices_all, normals_all, uv_all
                )
                if vertices is None:
                    continue 
                # Drop the initial usemtl from mts[0]
                mtl = materials[mts[0].strip().split(" ")[-1]]
                rparams_per_object.append({
                    "vertices": vertices,
                    "normals": normals,
                    "uv": uv,
                    "material": Material(
                        ambient=mtl["ambient"],
                        diffuse=mtl["diffuse"],
                        specular=mtl["specular"],
                        Ns=mtl["Ns"],
                        texture=mtl["texture"],
                        bump_map=mtl["bump"]
                    )}
                )
            else:
                chunks_per_material = get_chunks_from_list(lines_per_object, mts)
                for vk, ms_start, ms_end in chunks_per_material:
                    faces_lines = lines_per_object[ms_start + 1 : ms_end]
                    vertices, normals, uv = cls.collect_meshes(
                        lines_per_object, faces_lines,
                        vertices_all, normals_all, uv_all
                    )
                    if vertices is None:
                        continue 
                    mtl = materials[vk.strip().split(" ")[-1]]
                    rparams_per_object.append({
                        "vertices": vertices,
                        "normals": normals,
                        "uv": uv,
                        "material": Material(
                            ambient=mtl["ambient"],
                            diffuse=mtl["diffuse"],
                            specular=mtl["specular"],
                            Ns=mtl["Ns"],
                            texture=mtl["texture"],
                            bump_map=mtl["bump"]
                        )}
                    )
            # Now that we have collected all renderable_params for each object
            # we have to sort them based on which has a texture
            # rparams_per_object = sorted(
            #     rparams_per_object,
            #     key=lambda d: d["material"].texture is not None,
            #     reverse=True
            # )
            renderables_params.extend(rparams_per_object)

        close_file(filepath, f)
        return cls(renderables_params)
