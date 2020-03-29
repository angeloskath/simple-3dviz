# Creating Lights

simple-3dviz supports diffuse lighting. Diffuse lighting makes parts of the
objects facing the light brighter than the parts that are opposite from it.
Note that in contrast to ambient lighting, diffuse light is dependent on the
directions of the rays of lights. simple-3dviz allows you to change the
position of the light source.

```python
>>> from simple_3dviz import Mesh
>>> from simple_3dviz.window import show

>>> m = Mesh.from_file("models/baby_yoda.stl", color=(0.1, 0.8, 0.1))
# Scale the mesh such that it fits to  the unit cube [-0.5, 0.5]^3
>>> m.to_unit_cube()

# To better understand how our light works, we visualize the object as the
# lights moves across a circle.
>>> from simple_3dviz.behaviours.movements import LightTrajectory
>>> from simple_3dviz.behaviours.trajectory import Circle
>>> show(
...   m,
...   camera_position=(1, -1, 1),
...   behaviours=[
...     LightTrajectory(Circle((0, -1, 1), (2, -1, 1), (0, 0, 1)), speed=0.01)
...   ],
...   size=(256,256)
... )

# And also for a scenario that the light moves back and forth across a line
# segment
>>> from simple_3dviz.behaviours.trajectory import Lines
>>> from simple_3dviz.behaviours.trajectory import BackAndForth
>>> show(
...   m,
...   camera_position=(1, -1, 1),
...   behaviours=[
...     LightTrajectory(BackAndForth(Lines([1, -1, 1], [-1, 0, 1]), speed=0.05)
...   ],
...   size=(256,256)
... )
```

<div style="text-align: center;">
    <img src="../img/lights_circle.gif" alt="Light in Circle" />
    <img src="../img/lights_back_and_forth.gif" alt="Light Back and Forth" />
</div>
