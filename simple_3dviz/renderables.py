"""Renderables represent objects that can be rendered in a scene."""

import numpy as np
import trimesh

from .programs import uniform_value


class Renderable(object):
    """Represent something that can be rendered."""
    def init(self, ctx):
        """Initialize the renderable with the moderngl context."""
        raise NotImplementedError()

    def update_uniforms(self, uniforms):
        """Update any uniforms that are provided from somewhere else.
        
        The object is free to update its own programs' uniform values as well.
        Also since the program can be shared, the uniforms might be updated
        from another object.

        Arguments
        ---------
            uniforms: list of tuples
        """
        pass

    def render(self):
        """Render whatever this represents."""
        raise NotImplementedError()


class Circle(Renderable):
    def __init__(self, position=(0., 0.), radius=0.5, color=(0, 0, 0)):
        self._vertices = np.array([[-1,  1],
                                   [ 1,  1],
                                   [ 1, -1],
                                   [ 1, -1],
                                   [-1, -1],
                                   [-1,  1]], dtype="float32")
        self._radius = radius
        self._position = position
        self._color = color

        self._prog = None
        self._vao = None

        self.position = uniform_value(self, "_prog", "_position")
        self.radius = uniform_value(self, "_prog", "_radius")
        self.color = uniform_value(self, "_prog", "_color")

    def init(self, ctx):
        self._prog = ctx.program(
            vertex_shader="""
                #version 330

                in vec2 in_vert;
                out vec2 v_vert;

                void main() {
                    v_vert = in_vert;
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                }
                """,
            fragment_shader="""
                #version 330

                uniform float radius;
                uniform vec2 position;
                uniform vec3 color;
                in vec2 v_vert;
                out vec4 f_color;

                void main() {
                    float d = distance(v_vert, position);
                    float e = clamp(0.05*radius, 0.05, 0.1);
                    if (d < radius+e) {
                        float s = 1-smoothstep(radius-e, radius+e, d)/(radius+e);
                        f_color = vec4(color, s);
                    } else {
                        discard;
                    }
                }
                """
        )
        self._prog["radius"].value = self._radius
        self._prog["position"].value = self._position
        self._prog["color"].value = self._color
        vbo = ctx.buffer(self._vertices.tobytes())
        self._vao = ctx.simple_vertex_array(self._prog, vbo, "in_vert")

    def render(self):
        self._vao.render()


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


class Spherecloud(Renderable):
    def __init__(self, centers, colors, sizes):
        self._centers = centers
        self._colors = colors
        self._sizes = sizes

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

    def render(self):
        self._vao.render()

    def update_uniforms(self, uniforms):
        for k, v in uniforms:
            if k in ["light", "mvp", "vm"]:
                self._prog[k].write(v.tobytes())
