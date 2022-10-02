"""Load a material file into ambient, diffuse and specular colors and a set of
texture maps."""

import numpy as np
import os

from .utils import get_file, close_file
from ..utils import read_image


class MaterialReader(object):
    """MaterialReader defines the common interface for reading material files.
    """
    def __init__(self, filename=None):
        self._materials = {}
        self._current = None

        if filename is not None:
            self.read(filename)

    def read(self, filename):
        raise NotImplementedError()

    def set_material(self, name):
        self._current = name

    def has_material(self, name):
        return name in self._materials

    @property
    def material_names(self):
        return sorted(list(self._materials.keys()))

    @property
    def ambient(self):
        return self._materials[self._current]["ambient"]

    @property
    def diffuse(self):
        return self._materials[self._current]["diffuse"]

    @property
    def specular(self):
        return self._materials[self._current]["specular"]

    @property
    def Ns(self):
        return self._materials[self._current]["Ns"]

    @property
    def texture(self):
        return self._materials[self._current]["texture"]

    @property
    def bump_map(self):
        return self._materials[self._current]["bump"]

    @property
    def mode(self):
        return self._materials[self._current]["mode"]


class MtlMaterialReader(MaterialReader):
    """Read MTL material files."""
    def _read_texture(self, filename, texture_path):
        if isinstance(filename, str):
            return read_image(os.path.join(
                os.path.dirname(filename),
                texture_path
            ))
        else:
            if hasattr(filename, "name"):
                return read_image(os.path.join(
                    os.path.dirname(filename.name),
                    texture_path
                ))
            else:
                return None

    def read(self, filename):
        try:
            f = None
            f = get_file(filename)
            lines = f.readlines()

            materials = {}
            material = None
            for l in lines:
                l = l.strip()

                # Parse the name of the new mtl and add the previous to the
                # material list
                if l.startswith("newmtl"):
                    if material is not None:
                        materials[material["name"]] = material
                    material = {
                        "name": l.split()[1],
                        "ambient": np.array([1., 1, 1]),
                        "diffuse": np.array([1., 1, 1]),
                        "specular": np.array([0., 0, 0]),
                        "mode": "specular",
                        "Ns": 10.0,
                        "bump": None,
                        "texture": None
                    }

                # Collect the material color information, namely lines starting
                # with "Ka" followed by 3 floats indicating the r,g,b
                # components for the ambient reflectivity, "Kd" followed by 3
                # floats indicating the r,g,b components for the diffuse
                # reflectivity and "Ks" followed by 3 floats indicating the
                # r,g,b components for the specular reflectivity.
                elif l.startswith("Ka"):
                    material["ambient"] = np.array(
                        list(map(float, l.split()[1:]))
                    )

                elif l.startswith("Kd"):
                    material["diffuse"] = np.array(
                        list(map(float, l.split()[1:]))
                    )

                elif l.startswith("Ks"):
                    material["specular"] = np.array(
                        list(map(float, l.split()[1:]))
                    )

                # Collect the specular exponent, namely a line starting with
                # "Ns" followed by a float.
                elif l.startswith("Ns"):
                    material["Ns"] = float(l.split()[1])

                # Read the diffuse texture image
                elif l.startswith("map_Kd"):
                    material["texture"] = self._read_texture(
                        filename,
                        l.split()[1]
                    )

                # Read the bump map
                elif l.startswith("bump"):
                    material["bump"] = self._read_texture(
                        filename,
                        l.split()[1]
                    )

                # Collect the illumination model used for the material, namely
                # a line starting with "illum" and followed by an integer,
                # specifying the id of the illumination model.
                elif l.startswith("illum"):
                    material["mode"] = {
                        "0" : "constant",
                        "1" : "diffuse",
                        "2" : "specular"
                    }[l.split()[1]]

            if material is not None:
                materials[material["name"]] = material
                self._current = material["name"]

            self._materials = materials

        finally:
            if f is not None:
                close_file(filename, f)
