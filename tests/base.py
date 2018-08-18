"""Test basic instantiation and handling."""


# --- import --------------------------------------------------------------------------------------


import os

import WrightTools as wt


# --- test ----------------------------------------------------------------------------------------


def test_named_root_collection():
    c = wt.Collection(name="blaise")

def test_parent_child():
    parent = wt.Collection(name="mother")
    child = wt.Collection(parent=parent, name="goose")

def test_single_instance_collection():
    c1 = wt.Collection()
    c2 = wt.Collection(filepath=c1.filepath, edit_local=True)

def test_tempfile_cleanup():
    c = wt.Collection()
    path = c.filepath
    c.close()

