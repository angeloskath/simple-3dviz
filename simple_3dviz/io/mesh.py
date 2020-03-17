"""Load a mesh into three arrays vertices, faces and vertex_colors."""

import numpy as np
from plyfile import PlyData


class MeshReader(object):
    """MeshReader defines the common interface for reading all supported mesh
    files."""
    def __init__(self, filename=None):
        self._vertices = None
        self._vertex_normals = None
        self._faces = None
        self._face_colors = None

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
    def vertex_normals(self):
        if self._vertex_normals is None:
            raise NotImplementedError()
        return self._vertex_normals

    @property
    def faces(self):
        if self._faces is None:
            raise NotImplementedError()
        return self._faces

    @property
    def face_colors(self):
        if self._face_colors is None:
            raise NotImplementedError()
        return self._face_colors


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
                self._faces = np.vstack(data[F][VI])
            else:
                raise NotImplementedError(("Dealing with non-triangulated "
                                           "faces is not supported"))
            try:
                self._face_colors = np.zeros(
                    (data[F].count, 4),
                    dtype=np.float32
                )
                self._face_colors[:, 0] = data[F]["red"]
                self._face_colors[:, 1] = data[F]["green"]
                self._face_colors[:, 2] = data[F]["blue"]
                self._face_colors[:, 3] = 255
                try:
                    self._face_colors[:, 3] = data[F]["alpha"]
                except ValueError:
                    pass
                self._face_colors /= 255
            except ValueError:
                pass
