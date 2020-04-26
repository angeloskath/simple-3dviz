
import numpy as np

from .base import Renderable


class Spherecloud(Renderable):
    def __init__(self, centers, colors=(0.3, 0.3, 0.3), sizes=(0.02)):
        self._centers = np.asarray(centers)
        self._colors = np.asarray(colors)
        self._sizes = np.asarray(sizes)

        N = len(self._centers)
        if len(self._colors.shape) == 1:
            if self._colors.size == 3:
                self._colors = np.array(self._colors.tolist() + [1])
            self._colors = self._colors[np.newaxis].repeat(N, axis=0)
        elif self._colors.shape[1] == 3:
            self._colors = np.hstack([self._colors, np.ones((N, 1))])

        if len(self._sizes.shape) == 0:
            self._sizes = np.ones(N)*self._sizes

        self._prog = None
        self._vbo = None
        self._vao = None

    @property
    def packed_parameters(self):
        # Define the triangular pyramid assuming radius 1 and center 0 and then
        # offset and scale according to centers and sizes
        r2 = np.sqrt(2)
        r3 = np.sqrt(3)
        pyramid = np.array([[ 0,   r3,       0],
                            [ 1,    0,       0],
                            [-1,    0,       0],
                            [ 0, 1/r3, 2*r2/r3]])
        center = pyramid.mean(axis=0)
        ab = pyramid[1]-pyramid[0]
        ac = pyramid[2]-pyramid[0]
        normal = np.cross(ab, ac)
        normal /= np.sqrt(np.dot(normal, normal))
        max_radius = np.abs(np.dot(normal, pyramid[0]-center))
        pyramid -= center
        pyramid /= max_radius
        pyramid_vertices = pyramid[[0, 1, 2,
                                    0, 1, 3,
                                    0, 2, 3,
                                    1, 2, 3]][np.newaxis]

        vertices = self._sizes[:, np.newaxis, np.newaxis] * pyramid_vertices
        vertices += self._centers[:, np.newaxis]
        vertices = vertices.reshape(-1, 3)
        centers = np.repeat(self._centers, 12, axis=0)
        colors = np.repeat(self._colors, 12, axis=0)
        radii = np.repeat(self._sizes[:, np.newaxis], 12, axis=0)

        return np.hstack([vertices, centers, colors, radii]).astype(np.float32)

    def init(self, ctx):
        self._prog = ctx.program(
            vertex_shader="""
                #version 330

                uniform mat4 mvp;
                in vec3 in_vertex;
                in vec3 in_center;
                in vec4 in_color;
                in float in_radius;
                out vec3 v_vertex;
                out vec3 v_center;
                out vec4 v_color;
                out float v_radius;

                void main() {
                    v_vertex = in_vertex;
                    v_center = in_center;
                    v_color = in_color;
                    v_radius = in_radius;
                    gl_Position = mvp * vec4(in_vertex, 1);
                }
            """,
            fragment_shader="""
                #version 330

                uniform mat4 vm;
                uniform vec3 light;
                in vec3 v_vertex;
                in vec3 v_center;
                in vec4 v_color;
                in float v_radius;
                out vec4 f_color;

                void main() {
                    vec3 camera_position = vm[3].xyz / vm[3].w;
                    vec3 center_ray = v_center - camera_position;
                    vec3 ray = normalize(v_vertex - camera_position);
                    float tc = dot(center_ray, ray);
                    if (tc < 0) {
                        discard;
                    }
                    float d = sqrt(dot(center_ray, center_ray) - tc*tc);
                    if (d > v_radius) {
                        discard;
                    }
                    float t1c = sqrt(v_radius*v_radius - d*d);
                    vec3 p = camera_position + ray * (tc-t1c);

                    float lum = dot(
                        normalize(p - v_center),
                        normalize(p - light)
                    );
                    lum = acos(lum) / 3.14159265;
                    lum = clamp(lum, 0.0, 1.0);

                    f_color = vec4(v_color.xyz * lum, v_color.w);
                }
            """
        )
        self._vbo = ctx.buffer(self.packed_parameters.tobytes())
        self._vao = ctx.simple_vertex_array(
            self._prog,
            self._vbo,
            "in_vertex", "in_center", "in_color", "in_radius"
        )

    def sort_triangles(self, point):
        """Sort the triangles wrt point from further to closest."""
        centers = self._centers
        colors = self._colors
        sizes = self._sizes

        d = ((np.asarray(point).reshape(1, 3) - centers)**2).sum(-1)
        alpha = (colors[:, ::4].mean(-1)<1).astype(np.float32) * 1000
        idxs = np.argsort(d+alpha)[::-1]

        self._centers = centers[idxs]
        self._colors = colors[idxs]
        self._sizes = sizes[idxs]
        self._vbo.write(self.packed_parameters.tobytes())

    def release(self):
        self._prog.release()
        self._vbo.release()
        self._vao.release()

    def render(self):
        self._vao.render()

    def update_uniforms(self, uniforms):
        for k, v in uniforms:
            if k in ["light", "mvp", "vm"]:
                self._prog[k].write(v.tobytes())

    @property
    def bbox(self):
        """The axis aligned bounding box of all the vertices as two
        3-dimensional arrays containing the minimum and maximum for each
        axis."""
        return [
            self._centers.min(axis=0),
            self._centers.max(axis=0)
        ]

    def scale(self, s):
        """Multiply all the vertices with a number s."""
        self._centers *= s
        if self._vbo is not None:
            self._vbo.write(self.packed_parameters.tobytes())

    def to_unit_cube(self):
        """Transform the mesh such that it fits in the 0 centered unit cube."""
        bbox = self.bbox
        dims = bbox[1] - bbox[0]
        self._centers -= dims/2 + bbox[0]
        self._centers /= dims.max()
        if self._vbo is not None:
            self._vbo.write(self.packed_parameters.tobytes())
