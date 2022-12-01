import numpy as np

from ..utils import read_image
from .mesh import MeshBase, Mesh


class Image(MeshBase):
    """Render an image as a plane in the 3d scene.

    Arguments
    ---------
        image: A path to an image or a numpy array as returned by
               simple_3dviz.utils.read_image .
        position: The position of the center of the image.
        normal: The normal that defines the plane on which to draw the image.
        right_vector: The x-axis for the plane.
        size: The width and height of the image as a tuple.
        back: If set to True add a plane in the back to cover the image
        thickness: How thick should the image be in 3D
        backcolor: The color to use for the back of the image
    """
    def __init__(self, image, position=(0., 0, 0), normal=(0, -1., 0),
                 right_vector=(1, 0, 0.), size=(1., None)):
        if not isinstance(image, np.ndarray):
            image = read_image(image)

        size = list(size)
        if len(size) != 2:
            raise ValueError("Size should be a sequence with 2 elements")

        if size[0] is None and size[1] is None:
            raise ValueError(("At least one of the elements in size should "
                              "be a number"))

        height, width, _ = image.shape
        if size[0] is None:
            size[0] = width / height * size[1]
        if size[1] is None:
            size[1] = height / width * size[0]

        position, normal, right_vector, size = map(
            np.asarray, (position, normal, right_vector, size)
        )
        assert position.shape == (3,)
        assert normal.shape == (3,)
        assert right_vector.shape == (3,)
        assert size.shape == (2,)

        up_vector = np.cross(normal, right_vector)
        xleft = - size[0]/2 * right_vector
        xright = size[0]/2 * right_vector
        ybottom = - size[1]/2 * up_vector
        ytop = size[1]/2 * up_vector

        vertices = [
            position + xleft + ybottom,
            position + xright + ytop,
            position + xleft + ytop,

            position + xleft + ybottom,
            position + xright + ybottom,
            position + xright + ytop,
        ]
        uv = [
            [0, 0],
            [1, 1],
            [0, 1],

            [0, 0],
            [1, 0],
            [1, 1],
        ]

        #if back:
        #    eps = max(1e-5, thickness)
        #    vertices += [
        #        position + xleft + ybottom - eps * normal,
        #        position + xleft + ytop - eps * normal,
        #        position + xright + ytop - eps * normal,

        #        position + xleft + ybottom - eps * normal,
        #        position + xright + ytop - eps * normal,
        #        position + xright + ybottom - eps * normal,
        #    ]
        #    uv += [
        #        [0, 0],
        #        [0, 0],
        #        [0, 0],

        #        [0, 0],
        #        [0, 0],
        #        [0, 0],
        #    ]

        #if thickness > 0:
        #    vertices += [
        #        position + xleft + ybottom - thickness * normal,
        #        position + xleft + ytop,
        #        position + xleft + ytop - thickness * normal,

        #        position + xleft + ybottom - thickness * normal,
        #        position + xleft + ybottom,
        #        position + xleft + ytop,

        #        position + xright + ybottom - thickness * normal,
        #        position + xright + ytop - thickness * normal,
        #        position + xright + ytop,

        #        position + xright + ybottom - thickness * normal,
        #        position + xright + ytop,
        #        position + xright + ybottom,

        #        position + xleft + ytop - thickness * normal,
        #        position + xright + ytop,
        #        position + xright + ytop - thickness * normal,

        #        position + xleft + ytop - thickness * normal,
        #        position + xleft + ytop,
        #        position + xright + ytop,

        #        position + xleft + ybottom - thickness * normal,
        #        position + xright + ybottom - thickness * normal,
        #        position + xright + ybottom,

        #        position + xleft + ybottom - thickness * normal,
        #        position + xright + ybottom,
        #        position + xleft + ybottom,
        #    ]
        #    uv += [[0, 0]]*24

        vertices = np.asarray(vertices)
        normals = np.zeros_like(vertices)
        super().__init__(vertices, normals)

        self._uv = np.asarray(uv)

        self._image = image
        self._texture = None
        self._opacity = 0.2

    def init(self, ctx):
        self._prog = ctx.program(
            vertex_shader="""
                #version 330

                uniform mat4 mvp;
                uniform mat4 local_model;
                uniform vec3 offset;
                in vec3 in_vert;
                in vec2 in_uv;
                out vec3 v_vert;
                out vec2 v_uv;

                void main() {
                    vec4 t_pos = vec4(in_vert, 1.0);

                    t_pos = local_model * t_pos;
                    t_pos = t_pos + vec4(offset, 0);
                    vec3 g_pos = vec3(t_pos);
                    t_pos = mvp * t_pos;

                    // outputs
                    v_vert = g_pos;
                    v_uv = in_uv;
                    gl_Position = t_pos;
                }
            """,
            fragment_shader="""
                #version 330

                uniform float opacity;
                uniform sampler2D texture;

                in vec3 v_vert;
                in vec2 v_uv;

                out vec4 f_color;

                void main() {
                    vec4 texColor = texture2D(texture, v_uv);
                    f_color.rgb = texColor.rgb;
                    f_color.a = opacity;
                }
            """
        )
        self._vbo = ctx.buffer(np.hstack([
            self._vertices,
            self._uv
        ]).astype(np.float32).tobytes())
        self._vao = ctx.simple_vertex_array(
            self._prog,
            self._vbo,
            "in_vert", "in_uv"
        )
        self._prog["texture"] = 0
        self.model_matrix = self._model_matrix
        self.offset = self._offset
        self.image = self._image
        self.opacity = self._opacity

    def _get_uniforms_list(self):
        """Return the used uniforms to fetch from the scene."""
        return ["mvp"]

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, new_image):
        self._image = new_image
        if self._prog is None:
            return

        if self._texture is not None:
            self._texture.release()

        self._texture = self._prog.ctx.texture(
            self._image.shape[:2][::-1],
            self._image.shape[2],
            data=self._image[::-1].tobytes()
        )

    @property
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, new_opacity):
        self._opacity = new_opacity
        if self._prog:
            self._prog["opacity"] = self._opacity

    def render(self):
        self._texture.use(location=0)
        super().render()

    def release(self):
        if self._prog is not None:
            super().release()
            if self._texture is not None:
                self._texture.release()


class ImageFrame(Mesh):
    def __init__(self, image, position=(0., 0, 0), normal=(0, -1., 0),
                 right_vector=(1, 0, 0.), size=(1., None), thickness=0.02,
                 color=(0.3, 0.3, 0.3), padding=0.01):
        if not isinstance(image, np.ndarray):
            image = read_image(image)

        size = list(size)
        if len(size) != 2:
            raise ValueError("Size should be a sequence with 2 elements")

        if size[0] is None and size[1] is None:
            raise ValueError(("At least one of the elements in size should "
                              "be a number"))

        height, width, _ = image.shape
        if size[0] is None:
            size[0] = width / height * size[1]
        if size[1] is None:
            size[1] = height / width * size[0]

        position, normal, right_vector, size = map(
            np.asarray, (position, normal, right_vector, size)
        )
        assert position.shape == (3,)
        assert normal.shape == (3,)
        assert right_vector.shape == (3,)
        assert size.shape == (2,)

        up_vector = np.cross(normal, right_vector)
        xleft = (- size[0]/2 * right_vector) * (1 + padding)
        xright = (size[0]/2 * right_vector) * (1 + padding)
        ybottom = (- size[1]/2 * up_vector) * (1 + padding)
        ytop = (size[1]/2 * up_vector) * (1 + padding)

        vertices = np.asarray([
            position + xleft + ybottom - thickness * normal,
            position + xleft + ytop - thickness * normal,
            position + xright + ytop - thickness * normal,

            position + xleft + ybottom - thickness * normal,
            position + xright + ytop - thickness * normal,
            position + xright + ybottom - thickness * normal,

            position + xleft + ybottom - thickness * normal,
            position + xleft + ytop,
            position + xleft + ytop - thickness * normal,

            position + xleft + ybottom - thickness * normal,
            position + xleft + ybottom,
            position + xleft + ytop,

            position + xright + ybottom - thickness * normal,
            position + xright + ytop - thickness * normal,
            position + xright + ytop,

            position + xright + ybottom - thickness * normal,
            position + xright + ytop,
            position + xright + ybottom,

            position + xleft + ytop - thickness * normal,
            position + xright + ytop,
            position + xright + ytop - thickness * normal,

            position + xleft + ytop - thickness * normal,
            position + xleft + ytop,
            position + xright + ytop,

            position + xleft + ybottom - thickness * normal,
            position + xright + ybottom - thickness * normal,
            position + xright + ybottom,

            position + xleft + ybottom - thickness * normal,
            position + xright + ybottom,
            position + xleft + ybottom,
        ])
        normals = np.repeat(self._triangle_normals(vertices), 3, axis=0)

        super().__init__(vertices, normals, colors=color)
