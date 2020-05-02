"""
TBD
"""

# for argparse compatibility, make all public names from argparse importable from here
from argparse import *

from .parser import ArgumentParser
from .spec import register_spec

# register standard python types (e.g. datetime.date, pathlib.Path)
from . import types as _types

ArgumentParser, register_spec, _types  # pyflakes
