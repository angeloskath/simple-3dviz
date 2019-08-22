class BaseWindow(object):
    def __init__(self, size=(512, 512)):
        self.size = size
        self._behaviours = []

    def add_behaviours(self, behaviours):
        self._behaviours.extend(behaviours)
        return self

    def add_behaviour(self, behaviour):
        self._behaviours.append(behaviour)
        return self

    def show(self, title="Scene"):
        raise NotImplementedError()
