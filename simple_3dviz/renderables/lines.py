
import moderngl
import numpy as np

from ..io.voxels import read_binvox
from .base import Renderable


class Lines(Renderable):
    """A line is a collection of line segments with colors and a specific width.

    Arguments:
    ----------
        points: array-like, the points that compose the line segments.
        colors: array-like, per line-segment color as (r,g,b,a)
        width: float indicating the width of the line
    """
    def __init__(self, points, colors=(0.3, 0.3, 0.3, 1.0), width=0.4):
        self._points, self._colors = self._parse_points_and_colors(
            points, colors
        )
        self._width = width

        self._prog = None
        self._vbo = None
        self._vao = None

    def _parse_points_and_colors(self, points, colors):
        points = np.asarray(points)
        colors = np.asarray(colors)

        N = len(points)
        if len(colors.shape) == 1:
            if colors.size == 3:
                colors = np.array(colors.tolist() + [1])
            colors = colors[np.newaxis].repeat(N, axis=0)
        elif colors.shape[1] == 3:
            colors = np.hstack([colors, np.ones((N, 1))])

        return points, colors

    def init(self, ctx):
        self._prog = ctx.program(
            vertex_shader="""
                #version 330

                in vec3 in_vertex;
                in vec4 in_color;
                out vec4 v_color;

                void main() {
                    v_color = in_color;
                    gl_Position = vec4(in_vertex, 1);
                }
            """,
            geometry_shader="""
                #version 330

                layout(lines) in;
                layout(triangle_strip, max_vertices=4) out;

                uniform float width;
                uniform mat4 vm;
                uniform mat4 mvp;
                in vec4 v_color[];
                out vec4 t_color;

                void main() {
                    vec3 camera_position = vm[3].xyz / vm[3].w;
                    vec3 first_v = gl_in[0].gl_Position.xyz;
                    vec3 last_v = gl_in[1].gl_Position.xyz;

                    vec3 ray_first = normalize(camera_position - first_v);
                    vec3 ray_last = normalize(camera_position - last_v);
                    vec3 line = normalize(last_v - first_v);
                    vec3 offset_first = cross(ray_first, line)*width/2;
                    vec3 offset_last = cross(ray_last, line)*width/2;

                    gl_Position = mvp * vec4(first_v + offset_first, 1);
                    t_color = v_color[0];
                    EmitVertex();
                    gl_Position = mvp * vec4(first_v - offset_first, 1);
                    t_color = v_color[0];
                    EmitVertex();
                    gl_Position = mvp * vec4(last_v + offset_last, 1);
                    t_color = v_color[1];
                    EmitVertex();
                    gl_Position = mvp * vec4(last_v - offset_last, 1);
                    t_color = v_color[1];
                    EmitVertex();

                    EndPrimitive();
                }
            """,
            fragment_shader="""
                #version 330

                in vec4 t_color;
                out vec4 f_color;

                void main() {
                    f_color = t_color;
                }
            """
        )
        self._vbo = ctx.buffer(
            np.hstack([self._points, self._colors]).astype(np.float32).tobytes()
        )
        self._vao = ctx.simple_vertex_array(
            self._prog,
            self._vbo,
            "in_vertex", "in_color"
        )

    def release(self):
        self._prog.release()
        self._vbo.release()
        self._vao.release()

    def render(self):
        self._vao.render(moderngl.LINES)

    def update_uniforms(self, uniforms):
        for k, v in uniforms:
            if k in ["mvp", "vm"]:
                self._prog[k].write(v.tobytes())
        self._prog["width"].value = self._width

    def _update_vbo(self):
        if self._vbo is not None:
            self._vbo.write(np.hstack([
                self._points, self._colors
            ]).astype(np.float32).tobytes())

    @property
    def bbox(self):
        """The axis aligned bounding box of all the vertices as two
        3-dimensional arrays containing the minimum and maximum for each
        axis."""
        return [
            self._points.min(axis=0),
            self._points.max(axis=0)
        ]

    def to_unit_cube(self):
        bbox = self.bbox
        dims = bbox[1] - bbox[0]
        self._points -= dims/2 + bbox[0]
        self._points /= dims.max()
        self._update_vbo()

    def append(self, points, colors=(0.3, 0.3, 0.3)):
        points, colors = self._parse_points_and_colors(points, colors)
        self._points = np.vstack([self._points, points])
        self._colors = np.vstack([self._colors, colors])
        self._update_vbo()

    @classmethod
    def from_voxel_grid(cls, voxels, colors=(0.1, 0.1, 0.1), width=0.001,
                        bbox=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]]):
        """Create a voxel grid wire frame.

        Arguments
        ---------
            voxels: Array of 3D values, with truthy values indicating which
                    voxels to fill
        """
        # Make sure voxels, colors and bbox are arrays
        voxels, colors, bbox = list(map(np.asarray, [voxels, colors, bbox]))

        # Ensure that the voxel grid is indeed a 3D grid
        assert len(voxels.shape) == 3
        M, N, K = voxels.shape

        # Compute the size of each side
        sizes = 0.5 * (bbox[1] - bbox[0]) / [M, N, K]

        # Convert the indices to center coordinates
        x, y, z = np.indices((M, N, K)).astype(np.float32)
        x = x / M * (bbox[1][0] - bbox[0][0]) + bbox[0][0]
        y = y / N * (bbox[1][1] - bbox[0][1]) + bbox[0][1]
        z = z / K * (bbox[1][2] - bbox[0][2]) + bbox[0][2]
        centers = np.vstack([x[voxels], y[voxels], z[voxels]]).T

        # Create an array containing the cube edges
        edges = np.array([[-1, -1, -1], [ 1, -1, -1],
                          [ 1, -1, -1], [ 1,  1, -1],
                          [ 1,  1, -1], [-1,  1, -1],
                          [-1,  1, -1], [-1, -1, -1],
                          [-1, -1,  1], [ 1, -1,  1],
                          [ 1, -1,  1], [ 1,  1,  1],
                          [ 1,  1,  1], [-1,  1,  1],
                          [-1,  1,  1], [-1, -1,  1],
                          [-1, -1, -1], [-1, -1,  1],
                          [-1,  1, -1], [-1,  1,  1],
                          [ 1, -1, -1], [ 1, -1,  1],
                          [ 1,  1, -1], [ 1,  1,  1]]) * sizes

        # Finally create the edges of each cube
        points = centers[:, np.newaxis] + edges[np.newaxis]

        # Convert the colors to per edge color
        if len(colors.shape) == 1:
            colors = np.array([colors]*(points.size // 3))
        elif len(colors.shape) == 4:
            colors = colors[voxels]
            colors = np.repeat(colors, len(edges), axis=0)

        return cls(points.reshape(-1, 3), colors, width)

    @classmethod
    def from_binvox(cls, binvoxfile, colors=(0.1, 0.1, 0.1), width=0.001):
        """Create a wireframe for voxel grid read from a binvox file.

        Arguments
        ---------
            binvoxfile: str or file object that contains the voxelgrid data in
                        binvox format
            colors: The colors of the voxels to pass to from_voxel_grid().
            width: The width of the lines for the wireframe.
        """
        voxelgrid, translation, scale = read_binvox(binvoxfile)
        bbox = np.array([[0., 0, 0], [1, 1, 1]]) * scale + translation

        return cls.from_voxel_grid(voxelgrid, colors=colors, bbox=bbox,
                                   width=width)

    @classmethod
    def axes(cls, origin=(0, 0, 0), size=1.0, colors=None, width=0.01):
        """Create the three axes to be used as a reference.

        Arguments
        ---------
            origin: array-like (3,), the origin to put the axes to
                    (default: (0, 0, 0))
            size: float or array-like (3,), the size of the axes lines
                  (default: 1.)
            colors: None or array-like (3, 3 or 4), the colors to use for each
                    of the three axes (default: None)
            width: float, the width of the lines (default: 0.01)
        """
        # Normalize the colors argument
        colors = colors or [[0.8, 0.2, 0.2], [0.2, 0.8, 0.2], [0.2, 0.2, 0.8]]
        colors = np.asarray(colors)
        if len(colors.shape) == 1:
            colors = colors[None]
        if len(colors) == 1:
            colors = np.repeat(colors, 3, axis=0)
        elif len(colors) != 3:
            raise ValueError("colors should contain 1 or 3 colors")
        if colors.shape[1] == 3:
            colors = np.hstack([colors, np.ones((3, 1))])
        elif colors.shape[1] != 4:
            raise ValueError("colors should be either 3 or 4 values")
        colors = np.repeat(colors, 2, axis=0)
        assert colors.shape == (6, 4)

        # Normalize the size argument
        size = np.ones(3) * size
        assert size.shape == (3,)

        # Normalize the origin argument
        origin = np.asarray(origin)
        assert origin.shape == (3,)

        axes = np.array([[0, 0, 0],
                         [1, 0, 0],
                         [0, 0, 0],
                         [0, 1, 0],
                         [0, 0, 0],
                         [0, 0, 1.]]) * size  + origin

        return cls(axes, colors, width=width)
