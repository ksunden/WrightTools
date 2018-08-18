import weakref
from . import kit as wt_kit
class Group():
    def __init__(self, file=None, parent=None, name=None, **kwargs):
        weakref.finalize(self, self.close)
    def close(self):
        from .collection import Collection
