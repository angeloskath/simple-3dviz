# Overview

In addition, to the main library, we also provide two useful tools for
visualizing meshes and 2D functions:

- `mesh_viewer`: Script for visualizing meshes, whose path is given as an input.
- `func_viewer`: Script for visualizing functions given from the command line.

Moreover, we also provide various examples that better showcase the
functionalities of simple-3dviz.

## mesh_viewer

mesh_viewer allows you to visualize a mesh, whose path is given as an input
from the command line. It is possible to specify the camera parameters (position,
viewing direction and "up" vector), the position of the light as well as the
parameters of the launched window (size and background color). Moreover, it is
possible to save the content of the scene by pressing "ctrl + S".

```bash
mesh_viewer --help
usage: mesh_viewer [-h] [--size SIZE] [--background BACKGROUND]
                   [--camera_position CAMERA_POSITION]
                   [--camera_target CAMERA_TARGET] [--up UP] [--light LIGHT]
                   [--color COLOR] [--use_tab20] [--manual]
                   [--save_frame SAVE_FRAME] [--direct_render DIRECT_RENDER]
                   [--with_texture]
                   file [file ...]

Visualize meshes with simple_3dviz

positional arguments:
  file

optional arguments:
  -h, --help            show this help message and exit
  --size SIZE           The size of the window
  --background BACKGROUND, -b BACKGROUND
                        The rgba background color
  --camera_position CAMERA_POSITION, -c CAMERA_POSITION
                        The position of the camera
  --camera_target CAMERA_TARGET, -t CAMERA_TARGET
                        The target of the camera
  --up UP               The up vector
  --light LIGHT
  --color COLOR         Choose a color for the mesh
  --use_tab20           Use matplotlib's tab20 color map
  --manual              Auto determine the camera position and target
  --save_frame SAVE_FRAME
                        The location to save the snapshot frame
  --direct_render DIRECT_RENDER
                        If provided render to this file and exit
  --with_texture        Load mesh with texture
```

<div style="text-align: center;">
    <video controls width="100%">
        <source src="http://simple-3dviz.com/files/videos/mesh_viewer.mp4"
                type="video/mp4">
    </video>
</div>

## func_viewer

func_viewer allows you to visualize a function whose expression is given from
the command line. It is a simple tool that allows for fast visualization of
various 2D functions.

```bash
func_viewer --help
usage: func_viewer [-h] [--n_points N_POINTS] [--xlim XLIM] [--ylim YLIM]
                   [--colormap COLORMAP] [--log_colors] [--size SIZE]
                   [--background BACKGROUND]
                   [--camera_position CAMERA_POSITION]
                   [--camera_target CAMERA_TARGET] [--up UP] [--light LIGHT]
                   [--no_axes]
                   function

Visualize functions with simple_3dviz

positional arguments:
  function

optional arguments:
  -h, --help            show this help message and exit
  --n_points N_POINTS   How many points per dimension
  --xlim XLIM           The limits for the x axis
  --ylim YLIM           The limits for the y axis
  --colormap COLORMAP   Set the matplotlib colormap
  --log_colors          Use logspace for assigning the colors
  --size SIZE           The size of the window
  --background BACKGROUND, -b BACKGROUND
                        The rgba background color
  --camera_position CAMERA_POSITION, -c CAMERA_POSITION
                        The position of the camera
  --camera_target CAMERA_TARGET, -t CAMERA_TARGET
                        The target of the camera
  --up UP               The up vector
  --light LIGHT
  --no_axes             Do not show the axes
```

<div style="text-align: center;">
    <video controls width="100%">
        <source src="http://simple-3dviz.com/files/videos/func_viewer.mp4"
                type="video/mp4">
    </video>
</div>

## Examples

Below, is a quick list of various example scripts:

* [Render meshes](https://github.com/angeloskath/simple-3dviz/tree/master/examples/render_mesh.py)
* [Render lines and voxels](https://github.com/angeloskath/simple-3dviz/tree/master/examples/render_line_voxels.py)
* [Render voxels](https://github.com/angeloskath/simple-3dviz/tree/master/examples/render_voxels.py)
* [Render spherecloud](https://github.com/angeloskath/simple-3dviz/tree/master/examples/render_spherecloud.py)
* [Render primitives](https://github.com/angeloskath/simple-3dviz/tree/master/examples/render_primitives.py)
* [Movements and trajectories](https://github.com/angeloskath/simple-3dviz/tree/master/examples/movements.py)
* [Save frames](https://github.com/angeloskath/simple-3dviz/tree/master/examples/save_frames.py)



