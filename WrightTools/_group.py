"""Group base class."""


# --- import --------------------------------------------------------------------------------------


import shutil
import os
import sys
import pathlib
import weakref
import tempfile
import posixpath
import warnings

import numpy as np

import h5py

from . import kit as wt_kit


# --- define --------------------------------------------------------------------------------------




# --- class ---------------------------------------------------------------------------------------

class Group(h5py.Group):
    """Container of groups and datasets."""

    _instances = {}
    class_name = "Group"

    def __init__(self, file=None, parent=None, name=None, **kwargs):
        if file is None:
            return
        # parent
        if parent is None:
            parent = ""
        if parent == "":
            parent = posixpath.sep
            path = posixpath.sep
        else:
            path = posixpath.sep.join([parent, name])
        self.filepath = file.filename
        file.require_group(parent)
        file.require_group(path)
        h5py.Group.__init__(self, bind=file[path].id)
        self.fid = self.file.fid
        self.natural_name = name
        # attrs
        self.attrs["class"] = self.class_name
        # the following are populated if not already recorded

        parent = file[parent]


    def __new__(cls, *args, **kwargs):
        """New object formation handler."""
        # extract
        filepath = args[0] if len(args) > 0 else kwargs.get("filepath", None)
        parent = args[1] if len(args) > 1 else kwargs.get("parent", None)
        natural_name = args[2] if len(args) > 2 else kwargs.get("name", cls.class_name.lower())
        edit_local = args[3] if len(args) > 3 else kwargs.pop("edit_local", False)
        file = None
        tmpfile = None
        if isinstance(parent, h5py.Group):
            filepath = parent.filepath
            file = parent.file
            if hasattr(parent, "_tmpfile"):
                tmpfile = parent._tmpfile
            parent = parent.name
            edit_local = True
        if edit_local and filepath is None:
            raise Exception  # TODO: better exception
        if not edit_local:
            tmpfile = tempfile.mkstemp(prefix="", suffix=".wt5")
            p = tmpfile[1]
            if filepath:
                shutil.copyfile(src=str(filepath), dst=p)
        elif edit_local and filepath:
            p = filepath
        p = str(p)
        for i in cls._instances.keys():
            if i.startswith(os.path.abspath(p) + "::"):
                file = cls._instances[i].file
                if hasattr(cls._instances[i], "_tmpfile"):
                    tmpfile = cls._instances[i]._tmpfile
                break
        if file is None:
            file = h5py.File(p, "a")
        # construct fullpath
        if parent is None:
            parent = ""
            name = posixpath.sep
        else:
            name = natural_name
        fullpath = p + "::" + parent + name
        # create and/or return
        try:
            instance = cls._instances[fullpath]
        except KeyError:
            kwargs["file"] = file
            kwargs["parent"] = parent
            kwargs["name"] = natural_name
            instance = super(Group, cls).__new__(cls)
            cls.__init__(instance, **kwargs)
            cls._instances[fullpath] = instance
            if tmpfile:
                setattr(instance, "_tmpfile", tmpfile)
                weakref.finalize(instance, instance.close)
        return instance

    @property
    def fullpath(self):
        """Full path: file and internal structure."""
        return self.filepath + "::" + self.name


    def close(self):
        from .collection import Collection
        pass
