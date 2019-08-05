"""Utilities for programs and perhaps some simple defaults."""


def uniform_value(obj, program, variable):
    def getter():
        return getattr(obj, variable)

    def setter(v):
        setattr(obj, variable, v)
        getattr(obj, program)[variable[1:]].value = v

    return property(getter, setter)
