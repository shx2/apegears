"""
An improved ArgumentParser, fully compatible with the standard argparse.ArgumentParser.

You can simply start by replacing your import lines::

    import argparse            -->  import apegears
    from argparse import ...   -->  from apegears import ...

"""

# This is a fix for Issue13041 ("terminal width is not detected properly")
try:
    import os as _os
    import shutil as _shutil
    _os.environ.setdefault('COLUMNS', str(_shutil.get_terminal_size().columns))
except Exception:
    pass

# for argparse compatibility, make all public names from argparse importable from here
from argparse import *

from .parser import ArgumentParser, CALLER_DOC
from .spec import register_spec

from .iofile import FileType, fileinput

# register standard python types (e.g. datetime.date, pathlib.Path)
from . import types as _types

ArgumentParser, CALLER_DOC, register_spec, FileType, fileinput, _types  # pyflakes
