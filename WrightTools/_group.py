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


class MetaClass(type(h5py.Group)):
    def __call__(cls, *args, **kwargs):
        """Bypass normal construction."""
        return cls.__new__(cls, *args, **kwargs)


class Group(h5py.Group, metaclass=MetaClass):
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
        self.__n = 0
        self.fid = self.file.fid
        self.natural_name = name
        # attrs
        self.attrs["class"] = self.class_name
        for key, value in kwargs.items():
            try:
                if isinstance(value, pathlib.Path):
                    value = str(value)
                elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], str):
                    value = np.array(value, dtype="S")
                elif sys.version_info > (3, 6):
                    try:
                        value = os.fspath(value)
                    except TypeError:
                        pass  # Not all things that can be stored have fspath
                self.attrs[key] = value
            except TypeError:
                # some values have no native HDF5 equivalent
                message = "'{}' not included in attrs because its Type ({}) cannot be represented"
                message = message.format(key, type(value))
                warnings.warn(message)
        # the following are populated if not already recorded
        self.item_names

        parent = file[parent]
        if parent.name == self.name:
            pass  # at root, dont add to item_names
        elif self.natural_name.encode() not in parent.attrs["item_names"]:
            parent.attrs["item_names"] = np.append(
                parent.attrs["item_names"], self.natural_name.encode()
            )


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

    @property
    def item_names(self):
        """Item names."""
        if "item_names" not in self.attrs.keys():
            self.attrs["item_names"] = np.array([], dtype="S")
        return tuple(n.decode() for n in self.attrs["item_names"])


    def close(self):
        """Close the file that contains the Group.

        All groups which are in the file will be closed and removed from the
        _instances dictionaries.
        Tempfiles, if they exist, will be removed
        """
        from .collection import Collection

        path = os.path.abspath(self.filepath) + "::"
        for kind in (Collection, Group):
            rm = []
            for key in kind._instances.keys():
                if key.startswith(path):
                    rm.append(key)
            for key in rm:
                kind._instances.pop(key, None)

        if self.fid.valid > 0:
            # for some reason, the following file operations sometimes fail
            # this stops execution of the method, meaning that the tempfile is never removed
            # the following try case ensures that the tempfile code is always executed
            # ---Blaise 2018-01-08
            try:
                self.file.flush()
                try:
                    # Obtaining the file descriptor must be done prior to closing
                    fd = self.fid.get_vfd_handle()
                except (NotImplementedError, ValueError):
                    # only available with certain h5py drivers
                    # not needed if not available
                    pass

                self.file.close()
                try:
                    if fd:
                        os.close(fd)
                except OSError:
                    # File already closed, e.g.
                    pass
            except SystemError as e:
                warnings.warn("SystemError: {0}".format(e))
            finally:
                if hasattr(self, "_tmpfile"):
                    os.close(self._tmpfile[0])
                    os.remove(self._tmpfile[1])

    def flush(self):
        """Ensure contents are written to file."""
        self.file.flush()
