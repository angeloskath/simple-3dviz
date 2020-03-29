"""Behaviours decouple the changes of a scene with the management of a scene
(creation, rendering, etc.).

The behaviours allow for a simple and unified way to animate, save frames to
disk, interact with a mouse and keyboard. This means that you can write all
your domain logic in terms of behaviours and then render with or without a GUI
by using `simple_3dviz.window.show` or `simple_3dviz.utils.render`
respectively.
"""

class Behaviour(object):
    """Behaviour defines the interface that is implemented by all behaviours
    and provides simple helper classes to encapsulate the current scene
    configuration.

    In particular the interface is a single method
    `simple_3dviz.behaviours.Behaviour.behave` that accepts a single argument
    of type `simple_3dviz.behaviours.Behaviour.Params`. For details see the
    corresponding comments.
    """
    class Mouse(object):
        """Hold information about the mouse events.

        Example behaviours that use the mouse can be found in
        `simple_3dviz.behaviours.mouse`.

        Attributes
        ----------
            location: (x, y), a tuple of floats or integers containing the
                      location of the mouse in the screen
            left_pressed: bool, indicating whether the left button of the mouse
                          is currently pressed (or has been pressed once)
            middle_pressed: bool, indicating whether the middle button of the
                            mouse is currently pressed (or has been pressed
                            once)
            wheel_rotation: float | int, indicate the number of position
                            changes of the scroll wheel of the mouse, the sign
                            indicates the direction of rotation
        """
        def __init__(self, location, left_pressed, middle_pressed, wheel_rotation):
            self.location = location
            self.left_pressed = left_pressed
            self.middle_pressed = middle_pressed
            self.wheel_rotation = wheel_rotation

    class Keyboard(object):
        """Holds information about the keyboard events.

        The members are two sets containing string representations for the keys
        that were pressed down and released respectively. Example behaviours
        that use the keyboard can be found in
        `simple_3dviz.behaviours.keyboard` and
        `simple_3dviz.scripts.mesh_viewer`.

        Attributes
        ----------
            keys_down: set[string], the keys that were pressed down
            keys_up: set[string], the keys that were released
        """
        def __init__(self, keys_down, keys_up):
            self.keys_down = set(keys_down)
            self.keys_up = set(keys_up)

    class Params(object):
        """The parameters provided by the window to the behaviours.

        Attributes
        ----------
            window: A reference to the window object
            scene: A reference to the scene
            frame: A callable that returns the current frame
            mouse: A Behaviour.Mouse object providing mouse info
            keyboard: A Behaviour.Keyboard object providing keyboard info
            stop_propagation: bool, when set no more behaviours will be run
            done: bool, when set remove this behaviour from the list
            refresh: bool, when set make sure to redraw the window
        """
        def __init__(self, window, scene, frame, mouse, keyboard):
            self.window = window
            self.scene = scene
            self.frame = frame
            self.mouse = mouse
            self.keyboard = keyboard

            self._stop = False
            self._done = False
            self._refresh = False

        @property
        def stop_propagation(self):
            return self._stop

        @stop_propagation.setter
        def stop_propagation(self, s):
            self._stop = s

        @property
        def done(self):
            return self._done

        @done.setter
        def done(self, d):
            self._done = d

        @property
        def refresh(self):
            return self._refresh

        @refresh.setter
        def refresh(self, r):
            self._refresh = self._refresh or (r == True)

    def behave(self, params):
        raise NotImplementedError()


class SceneInit(Behaviour):
    """Initialize a scene.
    
    Run an init function once and update the render.
    """
    def __init__(self, scene_init):
        self._init_func = scene_init

    def behave(self, params):
        self._init_func(params.scene)
        params.done = True
        params.stop_propagation = True
        params.refresh = True
