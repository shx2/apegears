"""
An improved ArgumentParser, fully compatible with the standard argparse.ArgumentParser.

You can simply start by replacing your import lines::

    import argparse            -->  import apegears
    from argparse import ...   -->  from apegears import ...

"""

# for argparse compatibility, make all public names from argparse importable from here
from argparse import *

from .parser import ArgumentParser
from .spec import register_spec

from .iofile import FileType, fileinput

# register standard python types (e.g. datetime.date, pathlib.Path)
from . import types as _types

ArgumentParser, register_spec, FileType, fileinput, _types  # pyflakes
