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

