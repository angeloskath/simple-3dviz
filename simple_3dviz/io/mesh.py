"""Load a mesh into three arrays vertices, faces and vertex_colors."""

import numpy as np
from plyfile import PlyData

from ._utils import get_file, close_file


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

    def _get_colors(self, p):
        colors = np.zeros((p.count, 4), dtype=np.float32)
        colors[:, 0] = p["red"]
        colors[:, 1] = p["green"]
        colors[:, 2] = p["blue"]
        colors[:, 3] = 255
        try:
            colors[:, 3] = p["alpha"]
        except ValueError:
            pass
        colors /= 255
        return colors

    def read(self, filename):
        # Make local copies of the names of the ply elements
        V = self._names["vertex"]
        F = self._names["face"]
        VI = self._names["vertex_indices"]

        # Read the file into a PlyData datastucture
        data = PlyData.read(filename)

        # Get the vertices
        if V in data:
            self._vertices = np.vstack([
                data[V]["x"],
                data[V]["y"],
                data[V]["z"]
            ]).T

            # If we have per vertex colors get them as well
            per_vertex_colors = None
            try:
                per_vertex_colors = self._get_colors(data[V])
            except ValueError:
                pass
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
            if per_vertex_colors is not None:
                self._colors = per_vertex_colors[faces].reshape(-1, 4)
            else:
                try:
                    colors = self._get_colors(data[F])
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

        def triangulate_face(face):
            return [
                [face[0], face[i-1], face[i]]
                for i in range(2, len(face))
            ]

        try:
            f = get_file(filename)

            lines = f.readlines()

            # Collect all the vertices, namely lines starting with 'v' followed
            # by 3 floats and arrange them according to faces
            vertices = np.array([
                list(map(float, l.strip().split()[1:4]))
                for l in lines if l.startswith("v ")
            ], dtype=np.float32)
            faces = sum(
                [
                    triangulate_face(
                        list(map(extract_vertex, l.strip().split()[1:]))
                    ) for l in lines if l.startswith("f ")
                ],
                []
            )
            faces = np.array(faces)
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
        finally:
            close_file(filename, f)


class OffMeshReader(MeshReader):
    """Read OFF mesh files."""
    def read(self, filename):
        try:
            f = get_file(filename)

            # Read lines and clean them from comments and empty lines
            lines = f.readlines()
            lines = [l.strip() for l in lines if l[0]!="#" and l.strip() != ""]

            # Ensure it is an OFF file
            if not lines[0].startswith("OFF"):
                raise ValueError("Invalid OFF file.")

            # Extract the number of vertices, faces and edges
            if len(lines[0].split()) > 1:
                n_vertices, n_faces, n_edges = [
                    int(x)
                    for x in lines[0].split()[1:]
                ]
                lines = lines[1:]
            else:
                n_vertices, n_faces, n_edges = [
                    int(x)
                    for x in lines[1].split()
                ]
                lines = lines[2:]

            # Collect the vertices and faces
            vertices = np.array([
                [float(x) for x in l.split()]
                for l in lines[:n_vertices]
            ], dtype=np.float32)
            faces = np.array([
                [float(x) for x in l.split()]
                for l in lines[n_vertices:n_vertices+n_faces]
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
        finally:
            close_file(filename, f)


class StlMeshReader(MeshReader):
    """Read STL mesh files."""
    def read(self, filename):
        # Decide if it is an ASCII STL or not
        ascii_stl = True
        try:
            f = get_file(filename, "rb")
            try:
                past_header = str(f.read(100), encoding="ascii")
            except UnicodeDecodeError:
                ascii_stl = False
            f.seek(0)

            if ascii_stl:
                vertices = []
                normals = []
                START_SOLID = 1
                START_FACE = 2
                START_VERTEX = 3
                END_VERTEX = 4
                END_FACE = 5
                END_SOLID = 6
                normal = None
                state = START_SOLID
                for line in f:
                    line = str(line, encoding="ascii")
                    fields = line.strip().split()
                    if state == START_SOLID:
                        if fields[0] != "solid":
                            raise ValueError("Non ASCII STL")
                        state = START_FACE
                    elif state == START_FACE:
                        if fields[0] == "endsolid":
                            state = START_SOLID
                            continue
                        else:
                            assert fields[0] == "facet" and fields[1] == "normal"
                            normal = [float(x) for x in fields[2:5]]
                            state = START_VERTEX
                    elif state == START_VERTEX:
                        if fields[0] == "outer" and fields[1] == "loop":
                            continue
                        elif fields[0] == "vertex":
                            v = [float(x) for x in fields[1:4]]
                            vertices.append(v)
                            normals.append(normal)
                        elif fields[0] == "endloop":
                            state = END_FACE
                    elif state == END_FACE:
                        if fields[0] == "outer" and fields[1] == "loop":
                            state = START_VERTEX
                        else:
                            assert fields[0] == "endfacet"
                            state = START_FACE
                self._vertices = np.array(vertices)
                self._normals = np.array(normals)
            else:
                header = f.read(80)
                assert len(header) == 80
                triangles = np.frombuffer(f.read(4), "<i4", 1)[0]
                dtype = np.dtype([
                    ("normal", "<f4", (3,)),
                    ("vertices", "<f4", (3, 3)),
                    ("attr", "<u2")
                ])
                mesh = np.frombuffer(f.read(), dtype, triangles)
                self._vertices = mesh["vertices"].reshape(-1, 3)
                self._normals = np.repeat(mesh["normal"], 3, 0).reshape(-1, 3)
        finally:
            close_file(filename, f)
