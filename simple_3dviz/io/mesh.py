"""Load a mesh into three arrays vertices, faces and vertex_colors."""

import numpy as np
from plyfile import PlyData


class MeshReader(object):
    """MeshReader defines the common interface for reading all supported mesh
    files."""
    def __init__(self, filename=None):
        self._vertices = None
        self._normals = None
        self._colors = None

        if filename is not None:
            self.read(filename)

    def read(self, filename):
        raise NotImplementedError()

    @property
    def vertices(self):
        if self._vertices is None:
            raise NotImplementedError()
        return self._vertices

    @property
    def normals(self):
        if self._normals is None:
            raise NotImplementedError()
        return self._normals

    @property
    def colors(self):
        if self._colors is None:
            raise NotImplementedError()
        return self._colors


class PlyMeshReader(MeshReader):
    """Read binary or ascii PLY files."""
    def __init__(self, filename=None, vertex="vertex", face="face",
                 vertex_indices=None):
        self._names = {
            "vertex": vertex,
            "face": face,
            "vertex_indices": vertex_indices
        }
        super(PlyMeshReader, self).__init__(filename)

    def read(self, filename):
        V = self._names["vertex"]
        F = self._names["face"]
        VI = self._names["vertex_indices"]

        data = PlyData.read(filename)
        if V in data:
            self._vertices = np.vstack([
                data[V]["x"],
                data[V]["y"],
                data[V]["z"]
            ]).T
        if F in data:
            if VI is None:
                VI = data[F].properties[0].name
            triangles = sum(
                len(indices)-2
                for indices in data[F][VI]
            )
            if triangles == len(data[F][VI]):
                faces = np.vstack(data[F][VI])
            else:
                raise NotImplementedError(("Dealing with non-triangulated "
                                           "faces is not supported"))
            self._vertices = self._vertices[faces].reshape(-1, 3)
            try:
                colors = np.zeros(
                    (data[F].count, 4),
                    dtype=np.float32
                )
                colors[:, 0] = data[F]["red"]
                colors[:, 1] = data[F]["green"]
                colors[:, 2] = data[F]["blue"]
                colors[:, 3] = 255
                try:
                    colors[:, 3] = data[F]["alpha"]
                except ValueError:
                    pass
                colors /= 255
                self._colors = np.repeat(colors, 3, axis=0)
            except ValueError:
                pass


class ObjMeshReader(MeshReader):
    """Read OBJ mesh files."""
    def read(self, filename):
        def extract_vertex(face):
            return int(face.split("/")[0])-1

        def extract_normal(face):
            return int(face.split("/")[2])-1

        with open(filename, "r") as f:
            lines = f.readlines()

            # Collect all the vertices, namely lines starting with 'v' followed
            # by 3 floats and arrange them according to faces
            vertices = np.array([
                list(map(float, l.strip().split()[1:4]))
                for l in lines if l.startswith("v ")
            ], dtype=np.float32)
            faces = np.array([
                list(map(extract_vertex, l.strip().split()[1:]))
                for l in lines if l.startswith("f ")
            ])
            self._vertices = vertices[faces].reshape(-1, 3)

            # Collect all the vertex normals, namely lines starting with 'vn'
            # followed by 3 floats and arrange the according to faces
            try:
                normals = np.array([
                    list(map(float, l.strip().split()[1:]))
                    for l in lines if l.startswith("vn ")
                ])
                faces = np.array([
                    list(map(extract_normal, l.strip().split()[1:]))
                    for l in lines if l.startswith("f ")
                ])
                self._normals = normals[faces].reshape(-1, 3)
            except IndexError:
                pass


class OffMeshReader(MeshReader):
    """Read OFF mesh files."""
    def read(self, filename):
        with open(filename, "r") as f:
            lines = f.readlines()
            assert lines[0].strip() == "OFF"

            # Clean lines from comments and empty lines
            lines = [l.strip() for l in lines if l[0]!="#" and l.strip() != ""]

            # Extract the number of vertices and faces
            n_vertices, n_faces, n_edges = [int(x) for x in lines[1].split()]

            # Collect the vertices and faces
            vertices = np.array([
                [float(x) for x in l.split()]
                for l in lines[2:2+n_vertices]
            ], dtype=np.float32)
            faces = np.array([
                [float(x) for x in l.split()]
                for l in lines[2+n_vertices:2+n_vertices+n_faces]
            ], dtype=np.float32)

            if not np.all(faces[:, 0] == 3):
                raise NotImplementedError(("Dealing with non-triangulated "
                                           "faces is not supported"))

            # Set the triangles
            vertex_indices = faces[:, 1:4].astype(int).ravel()
            self._vertices = vertices[:, :3][vertex_indices]

            # Set the colors
            if vertices.shape[1] > 3:
                self._colors = vertices[:, 4:][vertex_indices]
            elif faces.shape[1] > 4:
                self._colors = np.repeat(faces[:, 4:], 3, axis=0)
