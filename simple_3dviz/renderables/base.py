import numpy as np


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


class RenderableCollection(Renderable):
    """Make many renderables behave like a single renderable."""

    def __init__(self, renderables):
        self.renderables = renderables

    def init(self, ctx):
        for r in self.renderables:
            r.init(ctx)

    def release(self):
        for r in self.renderables:
            r.release()

    def update_uniforms(self, uniforms):
        for r in self.renderables:
            r.update_uniforms(uniforms)

    def render(self):
        for r in self.renderables:
            r.render()

    @property
    def bbox(self):
        b_min = np.array([float("inf")]*3)
        b_max = -b_min
        for r in self.renderables:
            b_min_hat, b_max_hat = r.bbox
            b_min = np.minimum(b_min, b_min_hat)
            b_max = np.maximum(b_max, b_max_hat)
        return [b_min, b_max]

    def to_unit_cube(self):
        bbox = self.bbox
        dims = bbox[1] - bbox[0]
        translate = -(dims/2 + bbox[0])
        scale = 1/dims.max()

        for r in self.renderables:
            r.affine_transform(R=np.eye(3)*scale, t=scale*translate)
