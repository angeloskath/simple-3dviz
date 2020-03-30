# Creating Cameras

simple-3dviz supports a [perspective camera projection
model](http://www.cs.columbia.edu/~jebara/htmlpapers/SFM/node6.html). In
particular, we employ 
[pyrr](https://pyrr.readthedocs.io/en/latest/api_matrix.html#module-pyrr.matrix44)
for generating the correspondingprojection matrix, thus making it straight
forward to also implement other camera models.

To generate camera it simply suffices to specify its location
(`camera_position`), its viewing direction (`camera_target`) and the direction
that indicates which direction is "up" (`up_vector`).

```python
>>> from simple_3dviz import Mesh
>>> from simple_3dviz.window import show
>>> m = Mesh.from_file("models/penguin.stl", color=(0.8, 0.8, 0.8))
>>> m.to_unit_cube()

# Render the image with the default camera parameters
>>> show(
...    m,
...    camera_position=(-2, -2, -2),
...    camera_target=(0, 0, 0),
...    size=(256,256)
... )

# Let's move the camera closer and above the penguin
>>> show(
...    m,
...    camera_position=(-1, -1, -1),
...    camera_target=(0, 0, 0),
...    size=(256,256)
... )

# Let's move the camera a bit closer to the benguin
>>> show(
...    m,
...    camera_position=(-0.5, -0.5, -1),
...    camera_target=(0, 0, 0),
...    size=(256,256)
... )

# Let's now move both the up_vector and the camera_target
>>> show(
...    m,
...    camera_position=(-0.1, -2.0, 0.6),
...    camera_target=(0.0, 0.5, 0.0),
...    up_vector=(0.0, 0.22, 0.73),
...    size=(256,256)
... )
```

<div style="text-align: center;">
    <img src="../img/cameras_default.png" alt="Penguin 1" />
    <img src="../img/cameras_1.png" alt="Penguin 2" />
    <img src="../img/cameras_2.png" alt="Penguin 3" />
    <img src="../img/cameras_3.png" alt="Penguin 4" />
</div>

Note that by pressing the `R` key, when using the scene viewer via the `show`
function, simple-3dviz reports the camera configuration at the current
timestamp.
