"""Simple visualization of meshes using opengl with moderngl."""

__maintainer__ = "Angelos Katharopoulos, Despoina Paschalidou"
__email__ = "angelos.katharopoulos@idiap.ch"
__url__ = "http://simple-3dviz.com"
__description__ = "simple-3dviz is a simple visualization library for 3D "
"data using Python and OpenGL."
__keywords__ = "graphics geometry 3D"
__license__ = "MIT"
__version__ = "0.2.1"

from .renderables import Mesh, Spherecloud, Lines
from .scenes import Scene
from .utils import render
