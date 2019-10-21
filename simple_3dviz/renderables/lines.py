
import moderngl
import numpy as np

from .base import Renderable


class Lines(Renderable):
    def __init__(self, points, colors, width=1):
        self._points = np.asarray(points)
        self._colors = np.asarray(colors)
        self._width = width

        N = len(self._points)
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
