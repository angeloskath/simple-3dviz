"""Load a material file into ambient, diffuse and specular colors and a set of
texture maps."""

import numpy as np
import os

from .utils import _get_file, _close_file
from ..utils import read_image


class MaterialReader(object):
    """MaterialReader defines the common interface for reading material files.
    """
    def __init__(self, filename=None):
        self._name = None
        self._ambient = None
        self._diffuse = None
        self._specular = None
        self._Ns = None
        self._texture = None
        self._bump_map = None
        self._mode = None

        if filename is not None:
            self.read(filename)

    def read(self, filename):
        raise NotImplementedError()

    @property
    def ambient(self):
        if self._ambient is None:
            raise NotImplementedError()
        return self._ambient

    @property
    def diffuse(self):
        if self._diffuse is None:
            raise NotImplementedError()
        return self._diffuse

    @property
    def specular(self):
        if self._specular is None:
            raise NotImplementedError()
        return self._specular

    @property
    def Ns(self):
        if self._Ns is None:
            raise NotImplementedError()
        return self._Ns

    @property
    def texture(self):
        if self._texture is None:
            raise NotImplementedError()
        return self._texture

    @property
    def bump_map(self):
        if self._bump_map is None:
            raise NotImplementedError()
        return self._bump_map

    @property
    def mode(self):
        if self._mode is None:
            raise NotImplementedError()
        return self._mode

    def __getattribute__(self, key):
        if key.startswith("optional_"):
            key = key[9:]
            try:
                return getattr(self, key)
            except NotImplementedError:
                return None
        else:
            return super().__getattribute__(key)


class MtlMaterialReader(MaterialReader):
    """Read MTL material files."""
    def read(self, filename):
        try:
            f = None
            f = _get_file(filename)

            lines = f.readlines()

            # Collect the material color information, namely lines starting
            # with "Ka" followed by 3 floats indicating the r,g,b components
            # for the ambient reflectivity, "Kd" followed by 3 floats
            # indicating the r,g,b components for the diffuse reflectivity and
            # "Ks" followed by 3 floats indicating the r,g,b components for the
            # specular reflectivity.
            self._ambient = np.array([
                list(map(float, l.strip().split()[1:]))
                for l in lines if l.strip().startswith("Ka")
            ], dtype=np.float32)
            self._diffuse = np.array([
                list(map(float, l.strip().split()[1:]))
                for l in lines if l.strip().startswith("Kd")
            ], dtype=np.float32)
            self._specular = np.array([
                list(map(float, l.strip().split()[1:]))
                for l in lines if l.strip().startswith("Ks")
            ], dtype=np.float32)

            # Collect the specular exponent, namely a line starting with "Ns"
            # followed by a float.
            self._Ns = float([
                float(l.strip().split()[1:][0])
                for l in lines if l.strip().startswith("Ns")
            ][0])

            # Collect the information regarding texture maps and the bump map.
            try:
                texture_file = [
                    l.strip().split()[1:][0]
                    for l in lines if l.strip().startswith("map_Kd")
                ][0]

                if isinstance(filename, str):
                    self._texture = read_image(os.path.join(
                        os.path.dirname(filename),
                        texture_file
                    ))
                else:
                    if hasattr(filename, "name"):
                        self._texture = read_image(os.path.join(
                            os.path.dirname(filename.name),
                            texture_file
                        ))
                    else:
                        pass
            except IndexError:
                pass

            try:
                bump_map_file = [
                    l.strip().split()[1:][0]
                    for l in lines if l.strip().startswith("bump")
                ][0]
                if isinstance(filename, str):
                    self._bump_map = read_image(os.path.join(
                        os.path.dirname(filename),
                        bump_map_file
                    ))
                else:
                    if hasattr(filename, "name"):
                        self._bump_map = read_image(os.path.join(
                            os.path.dirname(filename.name),
                            bump_map_file
                        ))
                    else:
                        pass
            except IndexError:
                pass

            # Collect the illumination model used for the material, namely a
            # line starting with "illum" and followed by an integer, specifying
            # the id of the illumination model.
            self._mode = "specular"
            try:
                mode_id = [
                    l.strip().split()[1:][0]
                    for l in lines if l.strip().startswith("illum")
                ][0]
                self._mode = {
                    "0" : "constant",
                    "1" : "diffuse",
                    "2" : "specular",
                }[mode_id]
            except IndexError:
                pass

            # # Collect some additional informatation

            # # Transmission filter of the current material, namely a line
            # # starting with "Tf" followed by 3 floats indicating the r,g,b
            # # components of the atmosphere.
            # Tf = np.array([
            #     list(map(float, l.strip().split()[1:]))
            #     for l in lines if l.strip().startswith("Tf")
            # ], dtype=np.float32)

            # # Collect the dissolve for the current material, namely a line
            # # starting with "d" followed by a float, indicating the amount that
            # # this material dissolves into the background.
            # d = float([
            #     float(l.strip().split()[1:][0])
            #     for l in lines if l.strip().startswith("d")
            # ][0])

            # # Collect the optical density (index of refraction), namely a line
            # # starting with "Ni" followed by a float.
            # Ni = float([
            #     float(l.strip().split()[1:][0])
            #     for l in lines if l.strip().startswith("Ni")
            # ][0])

        finally:
            if f is not None:
                _close_file(filename, f)
