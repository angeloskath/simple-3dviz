
import numpy as np

from ..io import read_mesh_file, read_material_file
from .mesh import MeshBase


class Material(object):
    """A struct object containing information about the material.

    The supported materials have the following:

    - An ambient color
    - A diffuse lighting color (similar to `simple_3dviz.renderables.Mesh`)
    - A specular lighting color
    - A specular exponent for Phong lighting
    - A texture map
    - A bump map
    - A lighting mode from the set {'constant', 'diffuse', 'specular'}

    Arguments
    ---------
        ambient: array-like (r, g, b), float values between 0 and 1
        diffuse: array-like (r, g, b), float values between 0 and 1
        specular: array-like (r, g, b), float values between 0 and 1
        Ns: float, the exponent used for Phong lighting
        texture: array of uint8 with 3 or 4 channels and power of 2 width and
                 height, it contains the colors to be used by a mesh
        bump_map: array of uint8 with 3 channels and power of 2 width and
                  height, it contains the local displacement of the normal
                  vectors for implementing bump mapping
    """
    def __init__(self, ambient=(0., 0, 0), diffuse=(0.5, 0.5, 0.5),
                 specular=(0.5, 0.5, 0.5), Ns=10., texture=None,
                 bump_map=None, mode="specular"):
        self.ambient = np.asarray(ambient, dtype=np.float32)
        self.diffuse = np.asarray(diffuse, dtype=np.float32)
        self.specular = np.asarray(specular, dtype=np.float32)
        self.Ns = Ns
        self.texture = texture
        self.bump_map = bump_map
        if mode == "constant":
            self.diffuse[...] = 0
            self.specular[...] = 0
        elif mode == "diffuse":
            self.specular[...] = 0


class TexturedMesh(MeshBase):
    """A mesh that can use materials and textures to render a slightly more
    realistic image.

    Arguments
    ---------
        vertices: array-like, the vertices of the triangles. Each triangle
                  should be given on its own even if vertices are shared.
        normals: array-like, per vertex normal vectors
        uv: array-like, per-vertex uv coordinates inside the texture
        material: `simple_3dviz.renderables.Material` object
    """
    def __init__(self, vertices, normals, uv, material):
        super(TexturedMesh, self).__init__(vertices, normals)

        self._uv = np.asarray(uv)
        assert(self._uv.shape == (len(self._vertices), 2))
        self._material = material

        self._texture = None
        self._bump_map = None

    def init(self, ctx):
        self._prog = ctx.program(
            vertex_shader="""
                #version 330

                uniform mat4 mvp;
                uniform mat4 rotation;
                uniform mat4 local_model;
                uniform vec3 offset;
                in vec3 in_vert;
                in vec3 in_norm;
                in vec2 in_uv;
                out vec3 v_vert;
                out vec3 v_norm;
                out vec2 v_uv;

                void main() {
                    vec4 t_pos = vec4(in_vert, 1.0);
                    vec3 t_nor = in_norm;

                    t_pos = local_model * t_pos;
                    t_pos = t_pos + vec4(offset, 0);
                    t_pos = mvp * t_pos;

                    t_nor = mat3(local_model) * t_nor;
                    t_nor = mat3(rotation) * t_nor;

                    // outputs
                    v_vert = t_pos.xyz / t_pos.w;
                    v_norm = t_nor;
                    v_uv = in_uv;
                    gl_Position = t_pos;
                }
            """,
            fragment_shader="""
                #version 330

                uniform vec3 light;
                uniform vec3 camera_position;
                uniform vec3 ambient;
                uniform vec3 diffuse;
                uniform vec3 specular;
                uniform float Ns;
                uniform sampler2D texture;
                uniform sampler2D bump_map;
                uniform bool has_texture;
                uniform bool has_bump_map;
                in vec3 v_vert;
                in vec3 v_norm;
                in vec2 v_uv;

                out vec4 f_color;

                void main() {
                    // Local variables for the colors and normal
                    vec3 l_ambient = ambient;
                    vec3 l_diffuse = diffuse;
                    vec3 l_norm = v_norm;

                    // fix colors based on the textures
                    if (has_texture) {
                        vec4 texColor = texture2D(texture, v_uv);
                        l_ambient *= (1 - texColor.a);
                        l_ambient += texColor.a * texColor.rgb;
                        l_diffuse *= (1 - texColor.a);
                        l_diffuse += texColor.a * texColor.rgb;
                    }

                    // fix normal based on the bump map
                    if (has_bump_map) {
                        vec3 bump_normal = texture2D(bump_map, v_uv).rgb;
                        l_norm += (dot(v_norm, v_norm) - 1) * bump_normal;
                    }

                    // ambient color
                    f_color.rgb = l_ambient;

                    // diffuse color
                    vec3 L = normalize(light - v_vert);
                    f_color.rgb += l_diffuse * clamp(dot(l_norm, L), 0, 1);

                    // specular color
                    vec3 V = normalize(camera_position - v_vert);
                    vec3 H = normalize(L + V);
                    f_color.rgb += specular * pow(clamp(dot(l_norm, H), 0, 1), Ns);
                    f_color.a = 1.0;
                }
            """
        )
        self._vbo = ctx.buffer(np.hstack([
            self._vertices,
            self._normals,
            self._uv
        ]).astype(np.float32).tobytes())
        self._vao = ctx.simple_vertex_array(
            self._prog,
            self._vbo,
            "in_vert", "in_norm", "in_uv"
        )
        self._prog["texture"] = 0
        self._prog["bump_map"] = 1
        self.model_matrix = self._model_matrix
        self.offset = self._offset
        self.material = self._material

    def release(self):
        super(TexturedMesh, self).release()
        if self._texture is not None:
            self._texture.release()
        if self._bump_map is not None:
            self._bump_map.release()

    def _get_uniforms_list(self):
        """Return the used uniforms to fetch from the scene."""
        return ["light", "camera_position", "mvp", "rotation"]

    def _update_vbo(self):
        """Write in the vertex buffer object the vertices, normals and
        colors."""
        if self._vbo is not None:
            self._vbo.write(np.hstack([
                self._vertices, self._normals, self._uv, self._material
            ]).astype(np.float32).tobytes())

    @property
    def material(self):
        return self._material

    @material.setter
    def material(self, new_material):
        assert isinstance(new_material, Material)
        self._material = new_material
        if self._prog is None:
            return

        self._prog["ambient"].write(self._material.ambient.tobytes())
        self._prog["diffuse"].write(self._material.diffuse.tobytes())
        self._prog["specular"].write(self._material.specular.tobytes())
        self._prog["Ns"] = self._material.Ns
        if self._material.texture is not None:
            self._prog["has_texture"] = True
            if self._texture is not None:
                self._texture.release()
            self._texture = self._prog.ctx.texture(
                self._material.texture.shape[:2][::-1],
                self._material.texture.shape[2],
                data=self._material.texture.tobytes()
            )
        else:
            self._prog["has_texture"] = False
        if self._material.bump_map is not None:
            self._prog["has_bump_map"] = True
            if self._bump_map is not None:
                self._bump_map.release()
            self._bump_map = self._prog.ctx.texture(
                self._material.bump_map.shape[:2][::-1],
                self._material.bump_map.shape[2],
                data=self._material.bump_map.tobytes()
            )
        else:
            self._prog["has_bump_map"] = False

    def render(self):
        if self._texture is not None:
            self._texture.use(location=0)
        if self._bump_map is not None:
            self._bump_map.use(location=1)
        super(TexturedMesh, self).render()

    @classmethod
    def from_file(cls, filepath, material_filepath=None, ext=None,
                  material_ext=None):
        """Read the mesh from a file.

        Arguments
        ---------
            filepath: Path to file or file object containing the mesh
            material_filepath: Path to file containing the material
            ext: The file extension (including the dot) if 'filepath' is an
                 object
            material_ext: The file extension (including the dot) if 'filepath'
                          is an object
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

        # Set the uv coordinates
        try:
            uv = mesh.uv
        except NotImplementedError:
            uv = np.zeros(vertices.shape[0], 2)

        # Parse the material information
        mtl = None
        material = Material()
        try:
            mtl = read_material_file(mesh.material_file)
        except NotImplementedError:
            if material_filepath is not None:
                mtl = read_material_file(material_filepath, ext=material_ext)

        if mtl is not None:
            material = Material(
                ambient=mtl.ambient,
                diffuse=mtl.diffuse,
                specular=mtl.specular,
                Ns=mtl.Ns,
                texture=mtl.texture,
                bump_map=mtl.bump_map
            )

        return cls(vertices, normals, uv, material)
