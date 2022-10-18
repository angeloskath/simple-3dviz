"""Simple visualization of meshes using opengl with moderngl."""

__maintainer__ = "Angelos Katharopoulos, Despoina Paschalidou"
__email__ = "katharas@gmail.com"
__url__ = "http://simple-3dviz.com"
__description__ = "simple-3dviz is a simple visualization library for 3D "
"data using Python and OpenGL."
__keywords__ = "graphics geometry 3D"
__license__ = "MIT"
__version__ = "0.7.0"

from .renderables import Mesh, TexturedMesh, Spherecloud, Lines
from .scenes import Scene
from .utils import render
