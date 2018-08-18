"""WrightTools init."""
# flake8: noqa


# --- import --------------------------------------------------------------------------------------


import sys as _sys

from .__citation__ import *
from .__version__ import *
from .__wt5_version__ import *
from . import collection
from . import kit

from ._open import *
from .collection._collection import *
