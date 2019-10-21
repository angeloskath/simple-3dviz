class Renderable(object):
    """Represent something that can be rendered."""
    def init(self, ctx):
        """Initialize the renderable with the moderngl context."""
        raise NotImplementedError()

    def release(self):
        """Release all resources of this renderable in relation to open gl"""
        raise NotImplementedError()

    def update_uniforms(self, uniforms):
        """Update any uniforms that are provided from somewhere else.

        The object is free to update its own programs' uniform values as well.
        Also since the program can be shared, the uniforms might be updated
        from another object.

        Arguments
        ---------
            uniforms: list of tuples
        """
        pass

    def render(self):
        """Render whatever this represents."""
        raise NotImplementedError()

