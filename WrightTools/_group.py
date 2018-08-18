import weakref
import typing
class Group():
    def __init__(self):
        weakref.finalize(self, self.close)
    def close(self):
        from .collection import Collection
