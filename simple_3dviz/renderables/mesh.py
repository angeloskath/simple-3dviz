
import numpy as np

from .base import Renderable

try:
    import trimesh
except ImportError:
    pass


class Mesh(Renderable):
    def __init__(self, vertices, normals, colors):
        self._vertices = vertices
        self._normals = normals
        self._colors = colors

        self._prog = None
        self._vao = None

    def init(self, ctx):
        self._prog = ctx.program(
            vertex_shader="""
                #version 330

                uniform mat4 mvp;
                in vec3 in_vert;
                in vec3 in_norm;
                in vec3 in_color;
                out vec3 v_vert;
                out vec3 v_norm;
                out vec3 v_color;

                void main() {
                    v_vert = in_vert;
                    v_norm = in_norm;
                    v_color = in_color;
                    gl_Position = mvp * vec4(v_vert, 1.0);
                }
            """,
            fragment_shader="""
                #version 330

                uniform vec3 light;
                in vec3 v_vert;
                in vec3 v_norm;
                in vec3 v_color;

                out vec4 f_color;

                void main() {
                    float lum = dot(normalize(v_norm), normalize(v_vert - light));
                    lum = acos(lum) / 3.14159265;
                    lum = clamp(lum, 0.0, 1.0);

                    f_color = vec4(v_color * lum, 1.0);
                }
            """
        )
        vbo = ctx.buffer(np.hstack([
            self._vertices,
            self._normals,
            self._colors
        ]).astype(np.float32).tobytes())
        self._vao = ctx.simple_vertex_array(
            self._prog,
            vbo,
            "in_vert", "in_norm", "in_color"
        )

    def render(self):
        self._vao.render()

    def update_uniforms(self, uniforms):
        for k, v in uniforms:
            if k in ["light", "mvp"]:
                self._prog[k].write(v.tobytes())

    @staticmethod
    def _triangle_normals(triangles):
        triangles = triangles.reshape(-1, 3, 3)
        ba = triangles[:, 1] - triangles[:, 0]
        bc = triangles[:, 2] - triangles[:, 1]
        return np.cross(ba, bc, axis=-1)

    @classmethod
    def from_file(cls, filepath, color=None, use_vertex_normals=False):
        mesh = trimesh.load(filepath)
        vertices = mesh.vertices[mesh.faces.ravel()]
        if use_vertex_normals:
            normals = mesh.vertex_normals[mesh.faces.ravel()]
        else:
            normals = np.repeat(mesh.face_normals, 3, axis=0)
        if color is not None:
            colors = np.ones_like(vertices) * color
        elif mesh.visual is not None:
            colors = mesh.visual.vertex_colors[mesh.faces.ravel()]
            colors = colors[:, :3].astype(np.float32)/255

        return cls(vertices, normals, colors)

    @classmethod
    def from_xyz(cls, X, Y, Z, colormap=None):
        X, Y, Z = list(map(np.asarray, [X, Y, Z]))
        def gray(x):
            return np.ones((x.shape[0], 3))*x[:, np.newaxis]

        def normalize(x):
            xmin = x.min()
            xmax = x.max()
            return 2*(x-xmin)/(xmax-xmin) - 1

        def idx(i, j, x):
            return i*x.shape[1] + j

        # Normalize dimensions in [-1, 1]
        x = normalize(X)
        y = normalize(Y)
        z = normalize(Z)

        # Create faces by triangulating each quad
        faces = []
        for i in range(x.shape[0]-1):
            for j in range(y.shape[1]-1):
                # i, j; i, j+1; i+1; j+1
                # i, j; i+1, j; i+1; j+1
                faces.extend([
                    idx(i+1, j+1, x),
                    idx(i, j+1, x),
                    idx(i, j, x),
                    idx(i+1, j, x),
                    idx(i+1, j+1, x),
                    idx(i, j, x)
                ])

        vertices = np.vstack([x.ravel(), y.ravel(), z.ravel()]).T[faces]
        colors = (
            colormap(vertices[:, -1])[:, :3]
            if colormap else gray(vertices[:, -1])
        )
        normals = np.repeat(cls._triangle_normals(vertices), 3, axis=0)

        return cls(vertices, normals, colors)

    @classmethod
    def from_faces(cls, vertices, faces, colors):
        vertices, faces, colors = list(map(
            np.asarray,
            [vertices, faces, colors]
        ))
        vertices = vertices[faces].reshape(-1, 3)
        normals = np.repeat(cls._triangle_normals(vertices), 3, axis=0)
        colors = colors[faces].reshape(-1, 3)

        return cls(vertices, normals, colors)

    @classmethod
    def from_boxes(cls, centers, sizes, colors):
        """Create boxes.

        Arguments
        ---------
            centers: Array of 3 dimensional centers
            sizes: Array of 3 sizes per box that give, half the width, half the
                   depth, half the height
            colors: tuple for all boxes or array of colors per box
        """
        box = np.array([[-1, -1,  1],
                        [ 1, -1,  1],
                        [ 1,  1,  1],
                        [-1, -1,  1],
                        [ 1,  1,  1],
                        [-1,  1,  1],
                        [-1,  1, -1],
                        [ 1,  1,  1],
                        [-1,  1,  1],
                        [-1,  1, -1],
                        [ 1,  1, -1],
                        [ 1,  1,  1],
                        [-1,  1, -1],
                        [-1, -1,  1],
                        [-1,  1,  1],
                        [-1,  1, -1],
                        [-1, -1,  1],
                        [-1, -1, -1],
                        [ 1, -1, -1],
                        [ 1, -1,  1],
                        [ 1,  1,  1],
                        [ 1, -1, -1],
                        [ 1,  1, -1],
                        [ 1,  1,  1],
                        [ 1, -1, -1],
                        [-1, -1,  1],
                        [ 1, -1,  1],
                        [ 1, -1, -1],
                        [-1, -1,  1],
                        [-1, -1, -1],
                        [ 1, -1, -1],
                        [-1,  1, -1],
                        [ 1,  1, -1],
                        [ 1, -1, -1],
                        [-1,  1, -1],
                        [-1, -1, -1]]).astype(np.float32)

        normals = np.array([[ 0,  0,  1],
                            [ 0,  0,  1],
                            [ 0,  0,  1],
                            [ 0,  0,  1],
                            [ 0,  0,  1],
                            [ 0,  0,  1],
                            [ 0,  1,  0],
                            [ 0,  1,  0],
                            [ 0,  1,  0],
                            [ 0,  1,  0],
                            [ 0,  1,  0],
                            [ 0,  1,  0],
                            [-1,  0,  0],
                            [-1,  0,  0],
                            [-1,  0,  0],
                            [-1,  0,  0],
                            [-1,  0,  0],
                            [-1,  0,  0],
                            [ 1,  0,  0],
                            [ 1,  0,  0],
                            [ 1,  0,  0],
                            [ 1,  0,  0],
                            [ 1,  0,  0],
                            [ 1,  0,  0],
                            [ 0, -1,  0],
                            [ 0, -1,  0],
                            [ 0, -1,  0],
                            [ 0, -1,  0],
                            [ 0, -1,  0],
                            [ 0, -1,  0],
                            [ 0,  0, -1],
                            [ 0,  0, -1],
                            [ 0,  0, -1],
                            [ 0,  0, -1],
                            [ 0,  0, -1],
                            [ 0,  0, -1]]).astype(np.float32)

        centers, sizes, colors = list(map(
            np.asarray,
            [centers, sizes, colors]
        ))

        assert len(centers.shape) == 2 and centers.shape[1] == 3
        assert len(sizes.shape) == 2 and sizes.shape[1] == 3
        vertices = centers[:, np.newaxis]+sizes[:, np.newaxis]*box[np.newaxis]
        vertices = vertices.reshape(-1, 3)
        normals = np.repeat(normals, len(centers), axis=0)

        if len(colors.shape) == 1:
            if colors.size > 3:
                colors = colors[:3]
            colors = colors[np.newaxis].repeat(len(vertices), axis=0)
        elif colors.shape[1] == 4:
            colors = colors[:, :3]
        if len(colors) != len(vertices) and len(colors) == len(centers):
            colors = np.repeat(colors, len(box), axis=0)

        return cls(vertices, normals, colors)

