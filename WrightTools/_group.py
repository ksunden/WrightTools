import weakref
from . import kit as wt_kit
class Group():
    _instances = {}
    def __init__(self, file=None, parent=None, name=None, **kwargs):
        Group._instances[id(self)] = self
        weakref.finalize(self, self.close)

    def close(self):
        from .collection import Collection
