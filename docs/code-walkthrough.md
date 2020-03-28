# Code walkthrough

Simple-3dviz uses [moderngl][moderngl] to create OpenGL contexts, frame buffers
etc. However, ModernGL is a low level abstraction over OpenGL which means that
we get to decide how to manage the rendering pipeline ourselves. Moreover,
ModernGL does not provide rendering primitives which means that we need to
write our own shaders to render objects/scenes.

The following sections describe in high level the core parts of our rendering
pipeline. For details, e.g. argument names and types, follow the links to the
[API docs][api_docs] or read [the code][github].

## Scene

A [Scene][api_scene] is a representation of a scene to be rendered. It manages
the ModernGL context and defines things like the background color or the size
of the frame. The scene also provides information about the camera as well as
any lighting to the shader programs that actually do the rendering.

All scenes have the ability to contain several objects that can be rendered,
namely implement the [Renderable][api_renderable] interface, which can be added
or removed with the `add()` or `remove()` methods of a scene. When the
`render()` method of a scene is called the GPU actually renders all objects on
the framebuffer.

The main scene implementation of simple-3dviz contains a single perspective
camera and a single light source.

## Renderables

The classes that implement the [Renderable][api_renderable] interface actually
contain the code that renders objects in the frame. They get the _uniform_
values (see the GLSL docs for [uniforms][uniform_docs]) from the scene and they
must be somewhat compatible. For instance, in order for a scene light to have
any effect, the Renderable needs to have a GLSL shader that takes it into
account.

Simple-3dviz starts out with the following Renderables:

1. [Mesh][api_mesh] is the workhorse of most rendering pipelins and renders a
   number of triangles in the scene
2. [Spherecloud][api_spheres] renders a collection of 3D spheres of specific
   color and size.
3. [Lines][api_lines] renders a set of 3D lines with specific width and color.

## Window

Simple-3dviz, due to ModernGL providing the OpenGL context, does not require
any graphical user interface to be able to render scenes. However, in most
cases we want to explore a 3D model before settling towards an animation or
presentation.

The [BaseWindow][api_window] interface implementations take care of the
interaction between your code and the GUI. It is designed to be agnostic of the
actual GUI library that implements it. All changes in a GUI scene are done
using behaviours, which are explained below.

One implementation of BaseWindow is provided using `wxpython`.

## Behaviours

The goal of the [Behaviour][api_behaviour] interface is to decouple the changes
of a scene with the scene management (creation, rendering, etc.). The interface
defines simply a method `behave(params)` which is called every time that a
frame is rendered (this is traditionally called a _tick_). The argument
`params` is an instance of the class [Behaviour.Params][api_behaviour] which
provides to the behaviour all the necessary information:

* A window if it exists
* A scene object to be possibly altered
* Access to the frame for saving
* Objects to access mouse and keyboard information if available

The above design allows for many reusable behaviours that implement animations,
mouse interaction and more. A non-exhaustive list follows:

1. CameraTrajectory
2. CameraTargetTrajectory
3. LightTrajectory
4. SaveFrames
5. MouseRotate
6. MouseZoom
7. SnapshotOnKey

[moderngl]: https://moderngl.readthedocs.io/en/latest/
[api_scene]: /api-docs/scenes.html
[api_renderable]: /api-docs/renderables/index.html
[uniform_docs]: https://www.khronos.org/opengl/wiki/Uniform_(GLSL)
[api_mesh]: /api-docs/renderables/mesh.html
[api_spheres]: /api-docs/renderables/spherecloud.html
[api_lines]: /api-docs/renderables/lines.html
[api_window]: /api-docs/window/index.html
[api_behaviour]: /api-docs/behaviours/index.html
[api_docs]: /api-docs/
[github]: https://github.com/angeloskath/simple-3dviz
