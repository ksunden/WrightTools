"""Collection."""


# --- import --------------------------------------------------------------------------------------


from .._group import Group

import dask.array as da


# --- define --------------------------------------------------------------------------------------


__all__ = ["Collection"]


# --- classes -------------------------------------------------------------------------------------


class Collection(Group):
    """Nestable Collection of Data objects."""

    class_name = "Collection"
