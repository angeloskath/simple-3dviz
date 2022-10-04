from .behaviours import Behaviour
from .renderables import Renderable
from .scenes import Scene


try:
    import cv2
    import numpy as np

    def save_frame(path, frame):
        channels = frame.shape[-1]
        if channels == 1:
            cv2.imwrite(path, frame)

        # swap channels from rgb to bgr
        image_data = [frame[:, :, i] for i in range(channels)]
        image_data[0], image_data[2] = image_data[2], image_data[0]
        frame = np.stack(image_data, axis=-1)

        cv2.imwrite(path, frame)

    def read_image(path):
        img = cv2.imread(path, -1)
        if len(img.shape) == 2:
            img = img[..., None]
        channels = img.shape[-1]
        if channels == 1:
            return img


        # swap channels from bgr to rgb
        image_data = [img[:, :, i] for i in range(channels)]
        image_data[0], image_data[2] = image_data[2], image_data[0]
        return np.stack(image_data, axis=-1)

except ImportError:
    from PIL import Image
    import numpy as np

    def save_frame(path, frame):
        Image.fromarray(frame).save(path)

    def read_image(path):
        img = np.asarray(Image.open(path))
        if len(img.shape) == 2:
            img = img[..., None]
        return img


def render(renderables, behaviours, n_frames, size=(512, 512),
           background=(1,)*4, camera_position=(-2, -2, -2),
           camera_target=(0, 0, 0), up_vector=(0, 0, 1), light=None,
           scene=None):
    """Render a list of primitives for a given number of frames calling the
    passed behaviours after every frame.

    Arguments
    ---------
        renderables: list[Renderable] the renderables to be displayed in the
                     scene
        behaviours: list[Behaviour] a list of behaviours to animate the scene
                    and save the results
        n_frames: int the number of frames to render
        size: (w, h) the size of the window
        background: (r, g, b, a) the rgba tuple for the background
        camera_position: (x, y, z) the position of the camera
        camera_target: (x, y, z) the point that the camera looks at
        up_vector: (x, y, z) defines the floor and sky
        light: (x, y, z) defines the position of the light source
        scene: An optional scene to reuse
    """
    # Create the scene or clear it if it is provided
    if scene is None:
        scene = Scene(size=size)
    else:
        scene.clear()

    # Set up the scene
    scene.background = background
    scene.camera_position = camera_position
    scene.camera_target = camera_target
    scene.up_vector = up_vector
    scene.light = light if light is not None else camera_position

    # Add the primitives
    if not isinstance(renderables, (list, tuple)):
        renderables = [renderables]
    if not all(isinstance(r, Renderable) for r in renderables):
        raise ValueError(("render() expects one or more renderables as "
                          "parameters not {}").format(renderables))
    for r in renderables:
        scene.add(r)

    # Render the frames and run the behaviours
    # TODO: The following code duplicates some logic that can be found also in
    #       the implementations of BaseWindow. Investigate whether this could
    #       be refactored out.
    for frame in range(n_frames):
        # render
        scene.render()

        # run the behaviours
        params = Behaviour.Params(
            None,                 # we have no window
            scene,                # the scene
            lambda: scene.frame,  # return the frame if needed
            None,                 # no mouse
            None,                 # no keyboard
            frame == n_frames-1   # is this the last frame?
        )
        remove = []
        for i, b in enumerate(behaviours):
            b.behave(params)
            if params.done:
                remove.append(i)
                params.done = False
            if params.stop_propagation:
                break
        for i in reversed(remove):
            behaviours.pop(i)


def normalize_colors(c, N):
    """Normalize `c` so that it represents N 4-dimensional color values."""
    c = np.asarray(c)
    if len(c.shape) == 1:
        if c.shape[0] == 3:
            c = np.array(c.tolist() + [1.0])
        c = c[np.newaxis].repeat(N, axis=0)
    elif len(c.shape) == 2:
        if len(c) != N:
            raise ValueError(("c cannot represent the requested number "
                              "of colors"))
        if c.shape[1] == 3:
            c = np.hstack([c, np.ones((N, 1))])

    if c.shape != (N, 4):
        raise ValueError(("c cannot represent the requested number of colors"))

    return c.astype(np.float32)
