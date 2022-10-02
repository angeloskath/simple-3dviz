import numpy as np

from ..utils import read_image


class Material(object):
    """A struct object containing information about the material.

    The supported materials have the following:

    - An ambient color
    - A diffuse lighting color (similar to `simple_3dviz.renderables.mesh.Mesh`)
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
    def __init__(self, ambient=(1.0, 1.0, 1.0), diffuse=(1.0, 1.0, 1.0),
                 specular=(0.1, 0.1, 0.1), Ns=2., texture=None,
                 bump_map=None, mode="diffuse"):
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

    @property
    def texture_flipped(self):
        return self.texture[::-1]

    @property
    def bump_map_flipped(self):
        return self.bump_map[::-1]

    @classmethod
    def with_texture_image(cls, texture_path, ambient=(0.4, 0.4, 0.4),
                           diffuse=(0.4, 0.4, 0.4), specular=(0.1, 0.1, 0.1),
                           Ns=2., mode="specular"):
        return cls(
            ambient=ambient,
            diffuse=diffuse,
            specular=specular,
            Ns=Ns,
            texture=read_image(texture_path),
            mode=mode
        )
