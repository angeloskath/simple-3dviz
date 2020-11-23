
import numpy as np

from ..io import read_mesh_file
from ..io.voxels import read_binvox
from .base import Renderable

from pyrr import Matrix44, matrix44


class Mesh(Renderable):
    """A mesh is a collection of triangles with normals and colors.

    Arguments
    ---------
        vertices: array-like, the vertices of the triangles. Each triangle
                  should be given on its own even if vertices are shared.
        normals: array-like, per vertex normal vectors
        colors: array-like, per vertex color as (r, g, b) floats or
                (r, g, b, a) floats. If one color is given then it is assumed
                to be for all vertices.
        offset: A translation vector for all the vertices. It can be changed
                after construction to animate the object together with the
                `model_matrix` property.
    """
    def __init__(self, vertices, normals, colors, offset=[0, 0, 0.]):
        self._vertices = np.asarray(vertices)
        self._normals = np.asarray(normals)
        self._colors = np.asarray(colors)
        self._model_matrix = np.eye(4).astype(np.float32)
        self._offset = np.asarray(offset).astype(np.float32)

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
                uniform mat4 local_model;
                uniform vec3 offset;
                in vec3 in_vert;
                in vec3 in_norm;
                in vec4 in_color;
                out vec3 v_vert;
                out vec3 v_norm;
                out vec4 v_color;

                void main() {
                    v_color = in_color;

                    // Compute the position of the vertex
                    vec4 t_position = vec4(in_vert, 1.0);
                    t_position = local_model * t_position;
                    t_position = t_position + vec4(offset, 0.);
                    v_vert = t_position.xyz / t_position.w;
                    // TODO: We should probably use the global model matrix as
                    //       well but it is left for the future 
                    t_position = mvp * t_position;
                    gl_Position = t_position;

                    // Compute the normal of the vertex
                    vec4 t_normal = vec4(in_norm, 1.0);
                    t_normal = local_model * t_normal;
                    v_norm = t_normal.xyz / t_normal.w;
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
        self.model_matrix = self._model_matrix
        self.offset = self._offset

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

    @property
    def bbox(self):
        """The axis aligned bounding box of all the vertices as two
        3-dimensional arrays containing the minimum and maximum for each
        axis."""
        return [
            self._vertices.min(axis=0),
            self._vertices.max(axis=0)
        ]

    @property
    def model_matrix(self):
        """An affine transformation matrix (4x4) applied to the mesh before
        rendering. Can be changed to animate the mesh."""
        return self._model_matrix

    @model_matrix.setter
    def model_matrix(self, v):
        self._model_matrix = np.asarray(v).astype(np.float32)
        if self._prog:
            self._prog["local_model"].write(self._model_matrix.tobytes())

    def rotate_x(self, angle):
        """Helper function that multiplies the `model_matrix` with a rotation
        matrix around the x axis."""
        m = Matrix44.from_x_rotation(angle)
        self.model_matrix = m.dot(self.model_matrix)

    def rotate_y(self, angle):
        """Helper function that multiplies the `model_matrix` with a rotation
        matrix around the y axis."""
        m = Matrix44.from_y_rotation(angle)
        self.model_matrix = m.dot(self.model_matrix)

    def rotate_z(self, angle):
        """Helper function that multiplies the `model_matrix` with a rotation
        matrix around the z axis."""
        m = Matrix44.from_z_rotation(angle)
        self.model_matrix = m.dot(self.model_matrix)

    def rotate_axis(self, axis, angle):
        """Helper function that multiplies the `model_matrix` with a rotation
        matrix around the passed in axis."""
        m = matrix44.create_from_axis_rotation(axis, angle)
        self.model_matrix = m.dot(self.model_matrix)

    @property
    def offset(self):
        """A translation vector for the mesh vertices."""
        return self._offset

    @offset.setter
    def offset(self, v):
        self._offset = np.asarray(v).astype(np.float32)
        if self._prog:
            self._prog["offset"].write(self._offset.tobytes())

    def sort_triangles(self, point):
        """Sort the triangles such that the first is furthest from `point` and
        the last is the closest to `point`.

        It is used so that transparency works properly in OpenGL.
        """
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
        if self._vbo is not None:
            self._vbo.write(np.hstack([
                self._vertices, self._normals, self._colors
            ]).astype(np.float32).tobytes())

    def scale(self, s):
        """Multiply all the vertices with a number s."""
        self._vertices *= s
        if self._vbo is not None:
            self._vbo.write(np.hstack([
                self._vertices, self._normals, self._colors
            ]).astype(np.float32).tobytes())

    def translate(self, t):
        """Translate all the vertices with a vector t."""
        self._vertices += t
        if self._vbo is not None:
            self._vbo.write(np.hstack([
                self._vertices, self._normals, self._colors
            ]).astype(np.float32).tobytes())

    def to_unit_cube(self):
        """Transform the mesh such that it fits in the 0 centered unit cube."""
        bbox = self.bbox
        dims = bbox[1] - bbox[0]
        self._vertices -= dims/2 + bbox[0]
        self._vertices /= dims.max()
        if self._vbo is not None:
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
    def from_file(cls, filepath, color=(0.3, 0.3, 0.3), ext=None):
        """Read the mesh from a file.

        Arguments
        ---------
            filepath: Path to file or file object containing the mesh
            color: A default color to load if the information is not provided
                   in the file
            ext: The file extension (including the dot) if `filepath` is an
                 object
        """
        # Read the mesh
        mesh = read_mesh_file(filepath, ext=ext)

        # Extract the triangles
        vertices = mesh.vertices

        # Set a normal per triangle vertex
        try:
            normals = mesh.normals
        except NotImplementedError:
            normals = np.repeat(Mesh._triangle_normals(vertices), 3, axis=0)

        # Set a color per triangle vertex
        try:
            colors = mesh.colors
        except NotImplementedError:
            colors = np.ones((len(vertices), 1)) * color

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
            colormap(Z.ravel()[faces])
            if colormap else gray(z.ravel()[faces])
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
        if len(colors.shape) != 1:
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
        if len(sizes.shape) == 1:
            sizes = sizes[np.newaxis].repeat(len(centers), axis=0)
        vertices = centers[:, np.newaxis]+sizes[:, np.newaxis]*box[np.newaxis]
        vertices = vertices.reshape(-1, 3)
        normals = np.vstack([normals]*len(centers))

        if len(colors.shape) == 1:
            if colors.size < 4:
                colors = np.array(colors.tolist() + [1.]*(4-colors.size))
            colors = colors[np.newaxis].repeat(len(vertices), axis=0)
        if len(colors) != len(vertices) and len(colors) == len(centers):
            colors = np.repeat(colors, len(box), axis=0)

        return cls(vertices, normals, colors)

    @classmethod
    def from_voxel_grid(cls, voxels, sizes=None, colors=(0.3, 0.3, 0.3),
                        bbox=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]]):
        """ Create a voxel grid

        Arguments
        ---------
            voxels: Array of 3D values, with truthy values indicating which
                    voxels to fill
            colors: The colors of the voxels. If colors is a vector then
                    it is the same for all voxels. If it is a 4 dimensional
                    tensor then a color per voxel is assumed.
        """
        # Make sure voxels, colors and bbox are arrays
        voxels, colors, bbox = list(map(np.asarray, [voxels, colors, bbox]))

        # Ensure that the voxel grid is indeed a 3D grid
        assert len(voxels.shape) == 3
        M, N, K = voxels.shape

        # Clean and standardize the sizes
        if sizes is None:
            sizes = (bbox[1]-bbox[0]) * 0.48 / [M, N, K]
        else:
            sizes = np.asarray(sizes)

        # Convert the indices to center coordinates
        x, y, z = np.indices((M, N, K)).astype(np.float32)
        x = x / M * (bbox[1][0] - bbox[0][0]) + bbox[0][0]
        y = y / N * (bbox[1][1] - bbox[0][1]) + bbox[0][1]
        z = z / K * (bbox[1][2] - bbox[0][2]) + bbox[0][2]
        centers = np.vstack([x[voxels], y[voxels], z[voxels]]).T

        # Convert the sizes to per box sizes
        if len(sizes.shape) == 1:
            sizes = np.array([sizes for _ in range(len(centers))])
        elif len(sizes.shape) == 4:
            sizes = sizes[voxels]

        # Convert the colors to per box colors
        if len(colors.shape) == 1:
            colors = np.array([colors for _ in range(len(centers))])
        elif len(colors.shape) == 4:
            colors = colors[voxels]

        return cls.from_boxes(centers=centers, sizes=sizes, colors=colors)

    @classmethod
    def from_binvox(cls, binvoxfile, colors=(0.3, 0.3, 0.3)):
        """Create a voxel grid from a binvox file.

        For the format see https://patrickmin.com/binvox/binvox.html .
        
        Arguments
        ---------
            binvoxfile: str or file object that contains the voxelgrid data in
                        binvox format
            colors: The colors of the voxels to pass to from_voxel_grid().
        """
        voxelgrid, translation, scale = read_binvox(binvoxfile)
        bbox = np.array([[0., 0, 0], [1, 1, 1]]) * scale + translation

        return cls.from_voxel_grid(voxelgrid, colors=colors, bbox=bbox)

    @classmethod
    def from_superquadrics(cls, alpha, epsilon, translation, rotation, colors,
                           offset=[0, 0, 0.], vertex_count=10000):
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
        n = int(np.sqrt(vertex_count))
        eta = np.linspace(-np.pi/2, np.pi/2, n, endpoint=True)
        omega = np.linspace(-np.pi, np.pi, n, endpoint=True)
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

        return cls(vertices, normals, colors, offset)
