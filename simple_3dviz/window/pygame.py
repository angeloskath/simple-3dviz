import moderngl
import numpy as np
import pygame
from pyrr import Matrix44

from ..behaviours import Behaviour
from ..scenes import Scene
from .base import BaseWindow


class Window(BaseWindow):
    def __init__(self, size=(512, 512)):
        super().__init__(size)
        self._ctx = None
        self._scene = None
        self._mouse = Behaviour.Mouse(None, None, None, None)
        self._keyboard = Behaviour.Keyboard([], [])
        self._closing = False

    def _handle_resize(self, event):
        if self._ctx is None:
            return

        W, H = event.x, event.y
        pygame.display.set_mode(
            (W, H),
            pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE
        )
        self._ctx.viewport = (0, 0, W, H)
        self._scene.camera_matrix = (
            Matrix44.perspective_projection(45., W/H, 0.1, 1000)
        )

    def _handle_keyboard(self, events):
        modifiers = {
            pygame.K_LCTRL: "<ctrl>",
            pygame.K_RCTRL: "<ctrl>",
            pygame.K_LALT: "<alt>",
            pygame.K_RALT: "<alt>",
            pygame.K_LMETA: "<cmd>",
            pygame.K_RMETA: "<cmd>",
        }
        self._keyboard.keys_up.clear()
        for event in events:
            key = event.unicode
            code = event.key
            key = modifiers.get(code, key)
            if key != "":
                if event.type == pygame.KEYDOWN:
                    self._keyboard.keys_down.add(key)
                elif event.type == pygame.KEYUP:
                    self._keyboard.keys_down.remove(key)
                    self._keyboard.keys_up.add(key)

    def _handle_mouse(self, wheel_event=None):
        self._mouse.location = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed(3)
        self._mouse.left_pressed = pressed[0]
        self._mouse.middle_pressed = pressed[1]
        if wheel_event is not None:
            self._mouse.wheel_rotation += wheel_event.precise_y
        else:
            self._mouse.wheel_rotation = 0

    def _get_frame(self):
        W, H = pygame.display.get_surface().get_size()
        framebuffer = self._ctx.detect_framebuffer()
        return np.frombuffer(
            framebuffer.read(viewport=self._mgl_context.viewport, components=4),
            dtype=np.uint8
        ).reshape((H, W, 4))[::-1]

    def _behave(self):
        params = Behaviour.Params(
            self,
            self._scene,
            self._get_frame,
            self._mouse,
            self._keyboard,
            self._closing
        )

        # Run the behaviours
        remove = []
        for i, b in enumerate(self._behaviours):
            b.behave(params)
            if params.done:
                remove.append(i)
                params.done = False
            if params.stop_propagation:
                break

        # Remove the ones that asked to be removed
        for i in reversed(remove):
            self._behaviours.pop(i)

        # If we are closing, remove all behaviours
        if self._closing:
            self._behaviours.clear()

        # Return whether we should paint again
        return params.refresh

    def _draw(self):
        if self._scene is None:
            self._ctx = moderngl.create_context()
            self._ctx.enable(moderngl.BLEND)
            self._ctx.blend_func = (
                moderngl.SRC_ALPHA,
                moderngl.ONE_MINUS_SRC_ALPHA
            )
            self._scene = Scene(
                size=self.size,
                background=(0,)*4,
                ctx=self._ctx
            )
        self._scene.render()

    def show(self, title="Scene"):
        # Initialize the pygame window
        pygame.init()
        pygame.display.set_caption(title)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_PROFILE_MASK,
            pygame.GL_CONTEXT_PROFILE_CORE
        )
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG,
            True
        )
        pygame.display.set_mode(
            self.size,
            pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE
        )

        # Draw the first frame
        self._draw()

        # Implement the main window loop
        ticks = pygame.time.get_ticks()
        while not self._closing:
            # Process pygame events and translate them to simple_3dviz
            refresh = False
            wheel_event = None
            key_events = []
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._closing = True
                elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
                    key_events.append(event)
                elif event.type == pygame.MOUSEWHEEL:
                    wheel_event = event
                elif event.type == pygame.WINDOWRESIZED:
                    self._handle_resize(event)
                    refresh = True
            self._handle_keyboard(key_events)
            self._handle_mouse(wheel_event)

            # Apply the simple_3dviz behaviours
            refresh |= self._behave()
            # If needed redraw
            if refresh:
                self._draw()
                pygame.display.flip()

            # Make sure we are running at most at ~60fps
            wait = 16 - (pygame.time.get_ticks() - ticks)
            if wait > 0:
                pygame.time.wait(wait-1)
            ticks = pygame.time.get_ticks()

        pygame.quit()
