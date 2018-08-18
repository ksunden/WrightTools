"""Group base class."""


# --- import --------------------------------------------------------------------------------------


import weakref
import posixpath

import numpy as np


from . import kit as wt_kit


# --- define --------------------------------------------------------------------------------------




# --- class ---------------------------------------------------------------------------------------

class Group():
    """Container of groups and datasets."""

    _instances = {}
    class_name = "Group"

    def __init__(self, file=None, parent=None, name=None, **kwargs):
        # parent
        if parent is None:
            parent = ""
        if parent == "":
            parent = posixpath.sep
            path = posixpath.sep
        self.natural_name = name
        # the following are populated if not already recorded

        Group._instances[id(self)] = self
        weakref.finalize(self, self.close)

    def close(self):
        from .collection import Collection
        pass
