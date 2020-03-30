# Creating Scenes

A `Scene` contains the OpenGL content to be rendered and it defines various
scene properties such as the background color or the size of the frame to be
rendered. Moreover, the scene also keeps track of the camera parameters as well
as any lighting added in the scene. Note that the default `Scene` object
contains a single perspective camera and a single diffuse light.

All scenes have the ability to contain multiple objects that can be rendered.
It is possible to add and remove renderables in the scene using the `add()` and
`remove()` methods of a scene. Moreover, it is also possible to render all
objects on the framebuffer using the `render()` method of a scene.

To create a `Scene` it simply suffices to call the class constructor. You can
optionally specify the background color and the size of the framebuffer.

```python
>>> from simple_3dviz import Scene
>>> s = Scene()
>>> s.render()
# The default background is white and the default size of the framebuffer is
# (256, 256)
>>> s.frame
... array([[[255, 255, 255, 255],
...         [255, 255, 255, 255],
            ...
...         [255, 255, 255, 255]]], dtype=uint8)

# Now we create a scene with black backround and framebuffer size (512, 512)
>>> s = Scene(background=(0.0, 0.0, 0.0, 1.0), size=(512, 512))
```

## Adding Renderables

We can add objects to a scene simply using the `add()` method. Note that the
objects that can be added should implement the `Renderable` interface.

```python
>>> from simple_3dviz.renderables import Spherecloud

>>> import numpy as np
>>> import matplotlib.pyplot as plt
>>> t = np.linspace(0, 4 * np.pi, 20)
>>> x = np.sin(2 * t)
>>> y = np.cos(t)
>>> z = np.cos(2 * t)
>>> sizes = (2 + np.sin(t)) * 0.125
>>> centers = np.stack([x, y, z]).reshape(3, -1).T
>>> cmap = plt.cm.copper
>>> colors = cmap(np.random.choice(np.arange(500), centers.shape[0]))
# Create a renderable to be added in the scene
>>> r1 = Spherecloud(centers=centers, sizes=sizes, colors=colors)
>>> s.add(r1)

# Adjust the camera position
>>> s.camera_position = (-2.45, -3, 0.5)
>>> s.render()

# Save the framebuffer
>>> from simple_3dviz.utils import save_frame
>>> save_frame("scenes_renderable_1.png", scene.frame)

# Let's now add a mesh
>>> r2 = Mesh.from_file("models/baby_yoda.stl", color=(0.1, 0.8, 0.1))
>>> r2.to_unit_cube()
>>> s.add(r2)
>>> s.camera_position = (-0.3, -4, 0.1)
>>> s.render()
>>> save_frame("scenes_renderable_2.png", scene.frame)

# It is also possible to update the position of a mesh
>>> r2.rotate(35*np.pi/180)
>>> s.render()
>>> save_frame("scenes_renderable_3.png", scene.frame)
```

<div style="text-align: center;">
    <img src="../img/scenes_renderable_1.png" alt="Renderable 1" width=32.5% height=50%/>
    <img src="../img/scenes_renderable_2.png" alt="Renderable 2" width=32.5% height=50%/>
    <img src="../img/scenes_renderable_3.png" alt="Renderable 3" width=32.5% height=50%/>
</div>

## Removing Renderables

Finally, removing objects can be easily done with the `remove()` function:

```python
>>> s.remove(r1)
>>> s.render()
>>> save_frame("scenes_renderable_4.png", scene.frame)
```

<div style="text-align: center;">
    <img src="../img/scenes_renderable_4.png" alt="Renderable 4" width=32.5% height=50%/>
</div>
