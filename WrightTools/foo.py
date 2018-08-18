import weakref
import typing
class Foo():
    def __init__(self):
        weakref.finalize(self, self.close)
    def close(self):
        from . import bar
