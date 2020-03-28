# Loading and Manipulating Data

Being able to load and manipulate data is the first step towards rendering a
scene. simple-3dviz implements various `renderables`, such as meshes, pointclouds,
lines e.t.c that can be used for configuring different types of input.

# Creating Meshes

simple-3dviz allows you to configure a `Mesh` from a file, a set of vertices
and normals, a voxel grid and a set of geometric primitives, which we model
using superquadric surfaces.

```python
>>> from simple_3dviz import Mesh
>>> m = Mesh.from_file("models/sheep.stl")

# It is possible to load a mesh with any color you like
>>> m = Mesh.from_file("models/sheep.stl", color=(1, 1, 0))
>>> m = Mesh.from_file("models/sheep.stl", color=(0.3, 1, 0.3))

# It is also possible to manipulate the position of a mesh in a scene by
# properly adjusting its offset
>>> m = Mesh.from_file("models/sheep.stl", color=(0.8, 0.8, 0.8))
>>> m2 = Mesh.from_file("models/pig.stl", color=(0.8, 0.38, 0.58))
>>> m2.offset = (1.5*30, 0, 0)
```

<div style="text-align: center;">
    <img src="../img/load_models_sheep_gray.png" alt="Gray Sheep" />
    <img src="../img/load_models_sheep_yellow.png" alt="Yellow Sheep" />
    <img src="../img/load_models_sheep_green.png" alt="Green Sheep" />
    <img src="../img/load_models_sheep_and_pig.png" alt="Sheep and Pig" />
</div>

You can also create a `Mesh` from a set of vertices and normals.

```python
>>> import numpy as np
```

# Creating Voxel grids

It is possible to create a `Mesh` containing a voxel grid 

# Creating Voxel grids

Note that the supported file formats for the meshes are [Wavefront
OBJ](https://en.wikipedia.org/wiki/Wavefront_.obj_file), [ASCII
OFF](https://people.sc.fsu.edu/~jburkardt/data/off/off.html), [binary/ASCII
STL](https://en.wikipedia.org/wiki/STL_(file_format)) and [binary/ASCII
PLY](http://paulbourke.net/dataformats/ply/).


