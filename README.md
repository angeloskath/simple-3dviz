simple-3dviz
---------------

simple-3dviz provides a set of simple and reusable tools for visualizing 3D
data using Python and OpenGL. The goal of this library is to provide an easy
way to visualize 3D objects with thousands of vertices efficiently just with
few lines of code. 

Key features include:
- Manipulation of meshes from [Wavefront OBJ](https://en.wikipedia.org/wiki/Wavefront_.obj_file), [ASCII OFF](https://people.sc.fsu.edu/~jburkardt/data/off/off.html) and [binary/ASCII PLY](http://paulbourke.net/dataformats/ply/).
- A lightweight and easy-to-use scene viewer using [wxpython](https://wxpython.org/) with support for animation and storing images.
- An offscreen rendering module.
- Easy-to-change shaders for meshes, pointclouds and lines.

## Dependencies & Installation

You can install `simple-3dviz` directly from `pip`.
```bash
pip install simple-3dviz
```
If you want to extend our code clone the repository and install it in
development mode. In addition to the main library, there are also two useful
console applications that can be used for visualizing meshes
([mesh_viewer](https://github.com/angeloskath/simple-3dviz/scripts/mesh_viewer.py))
and functions given from the command line
([func_viewer](https://github.com/angeloskath/simple-3dviz/scripts/func_viewer.py)).

The dependencies of `simple-3dviz` are listed below:
- [numpy](http://www.numpy.org/)
- [pyrr](https://github.com/adamlwgriffiths/Pyrr)
- [moderngl](https://github.com/moderngl/moderngl)
- [wxpython](https://wxpython.org/) (if you want to have a GUI)
- [PIL](https://pillow.readthedocs.io/en/stable/index.html) or [OpenCV](https://opencv.org/) (if you want to store the rendering to image files)


## Quick Start

You can find various examples of how to use our library in the provided
[scripts](https://github.com/angeloskath/simple-3dviz/scripts). Below is a
concise example that showcases the different features of `simple-3dviz`.

```python
from simple_3dviz import Mesh
```

## Documentation

The module has a dedicated [documentation site](http://simple-3dviz.com) but
you can also read the [source
code](https://github.com/angeloskath/simple-3dviz) and the
[examples](https://github.com/angeloskath/simple-3dviz) to get an idea of how
the library should be used and extended.

## License

Our code is released under the [MIT
license](https://github.com/angeloskath/LICENSE), which practically allows
anyone to do anything with it.
