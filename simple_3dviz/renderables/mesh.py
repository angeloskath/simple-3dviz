
import numpy as np

from .base import Renderable

try:
    import trimesh
except ImportError:
    pass


class Mesh(Renderable):
    def __init__(self, vertices, normals, colors):
        self._vertices = np.asarray(vertices)
        self._normals = np.asarray(normals)
        self._colors = np.asarray(colors)

        N = len(self._vertices)
        if len(self._colors.shape) == 1:
            if self._colors.size == 3:
                self._colors = np.array(self._colors.tolist() + [1])
            self._colors = self._colors[np.newaxis].repeat(N, axis=0)
        elif self._colors.shape[1] == 3:
            self._colors = np.hstack([self._colors, np.ones((N, 1))])

        self._prog = None
        self._vbo = None
        self._vao = None

    def init(self, ctx):
        self._prog = ctx.program(
            vertex_shader="""
                #version 330

                uniform mat4 mvp;
                in vec3 in_vert;
                in vec3 in_norm;
                in vec4 in_color;
                out vec3 v_vert;
                out vec3 v_norm;
                out vec4 v_color;

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
                in vec4 v_color;

                out vec4 f_color;

                void main() {
                    float lum = dot(normalize(v_norm), normalize(v_vert - light));
                    lum = acos(lum) / 3.14159265;
                    lum = clamp(lum, 0.0, 1.0);

                    f_color = vec4(v_color.xyz * lum, v_color.w);
                }
            """
        )
        self._vbo = ctx.buffer(np.hstack([
            self._vertices,
            self._normals,
            self._colors
        ]).astype(np.float32).tobytes())
        self._vao = ctx.simple_vertex_array(
            self._prog,
            self._vbo,
            "in_vert", "in_norm", "in_color"
        )

    def release(self):
        self._prog.release()
        self._vbo.release()
        self._vao.release()

    def render(self):
        self._vao.render()

    def update_uniforms(self, uniforms):
        for k, v in uniforms:
            if k in ["light", "mvp"]:
                self._prog[k].write(v.tobytes())

    def sort_triangles(self, point):
        """Sort the triangles wrt point from further to closest."""
        vertices = self._vertices.reshape(-1, 3, 3)
        normals = self._normals.reshape(-1, 9)
        colors = self._colors.reshape(-1, 12)

        centers = vertices.mean(-2)
        d = ((np.asarray(point).reshape(1, 3) - centers)**2).sum(-1)
        alpha = (colors[:, ::4].mean(-1)<1).astype(np.float32) * 1000
        idxs = np.argsort(d+alpha)[::-1]

        self._vertices = vertices[idxs].reshape(-1, 3)
        self._normals = normals[idxs].reshape(-1, 3)
        self._colors = colors[idxs].reshape(-1, 4)
        self._vbo.write(np.hstack([
            self._vertices, self._normals, self._colors
        ]).astype(np.float32).tobytes())

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
            colors = colors[:, :4].astype(np.float32)/255

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
            if colors.size < 4:
                colors = np.array(colors.tolist() + [1.]*(4-colors.size))
            colors = colors[np.newaxis].repeat(len(vertices), axis=0)
        if len(colors) != len(vertices) and len(colors) == len(centers):
            colors = np.repeat(colors, len(box), axis=0)

        return cls(vertices, normals, colors)

    @classmethod
    def from_superquadrics(cls, alpha, epsilon, translation, rotation, colors):
        """Create Superquadrics.

        Arguments
        ---------
            alpha: Array of 3 sizes, along each axis
            epsilon: Array of 2 shapes, along each a
            translation: Array of 3 dimensional center
            rotation: Array of size 3x3 containing the rotations
            colors: Tuple for all sqs or array of colors per sq
        """
        def fexp(x, p):
            return np.sign(x)*(np.abs(x)**p)

        def sq_surface(a1, a2, a3, e1, e2, eta, omega):
            x = a1 * fexp(np.cos(eta), e1) * fexp(np.cos(omega), e2)
            y = a2 * fexp(np.cos(eta), e1) * fexp(np.sin(omega), e2)
            z = a3 * fexp(np.sin(eta), e1)
            return x, y, z

        # triangulate the sphere to be used with the SQs
        eta = np.linspace(-np.pi/2, np.pi/2, 100, endpoint=True)
        omega = np.linspace(-np.pi, np.pi, 100, endpoint=True)
        triangles = []
        for o1, o2 in zip(np.roll(omega, 1), omega):
            triangles.extend([
                (eta[0], 0),
                (eta[1], o2),
                (eta[1], o1),
            ])
        for e in range(1, len(eta)-2):
            for o1, o2 in zip(np.roll(omega, 1), omega):
                triangles.extend([
                    (eta[e], o1),
                    (eta[e+1], o2),
                    (eta[e+1], o1),
                    (eta[e], o1),
                    (eta[e], o2),
                    (eta[e+1], o2),
                ])
        for o1, o2 in zip(np.roll(omega, 1), omega):
            triangles.extend([
                (eta[-1], 0),
                (eta[-2], o1),
                (eta[-2], o2),
            ])
        triangles = np.array(triangles)
        eta, omega = triangles[:, 0], triangles[:, 1]

        # collect the pretriangulated vertices of each SQ
        vertices = []
        a, e, t, R = list(map(
            np.asarray,
            [alpha, epsilon, translation, rotation]
        ))
        M, _ = a.shape  # number of superquadrics
        assert R.shape == (M, 3, 3)
        assert t.shape == (M, 3)
        for i in range(M):
            a1, a2, a3 = a[i]
            e1, e2 = e[i]
            x, y, z = sq_surface(a1, a2, a3, e1, e2, eta, omega)
            # Get points on the surface of each SQ
            V = np.stack([x, y, z], axis=-1)
            V = R[i].T.dot(V.T).T + t[i].reshape(1, 3)
            vertices.append(V)

        # Finalize the mesh
        vertices = np.vstack(vertices)
        normals = np.repeat(cls._triangle_normals(vertices), 3, axis=0)
        colors = np.asarray(colors)

        if len(colors.shape) == 1:
            if colors.size < 4:
                colors = np.array(colors.tolist() + [1.]*(4-colors.size))
            colors = colors[np.newaxis].repeat(len(vertices), axis=0)
        assert len(colors) == len(vertices) or len(colors) == M
        if len(colors) == M:
            colors = np.repeat(colors, len(vertices) // M, axis=0)

        return cls(vertices, normals, colors)

