class Behaviour(object):
    class Mouse(object):
        """Hold information about the current mouse events.

        TODO: This class should be augmented with more capabilities in due
              time.

        WARNING: The API most definitely will change.
        """
        def __init__(self, location, left_pressed, wheel_rotation):
            self.location = location
            self.left_pressed = left_pressed
            self.wheel_rotation = wheel_rotation

    class Keyboard(object):
        """Holds information about the keyboard events.

        The members are two sets containing the keys that were pressed down and
        released respectively.
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
