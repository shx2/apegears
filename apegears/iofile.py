"""
Tools for defining arguments involving reading and writing files.
"""

import os
import fileinput as _fileinput


################################################################################
# fileinput

class FileInputType:
    """
    A ``fileinput`` arg type.

    Typically used like::

        from apegears import fileinput
        parser.add_positional(type=fileinput(), nargs='*')

    :note:
        can also be used with different values of ``nargs``, and also in an optional
        (``add_list``, ``add_optional``).
    """

    def __init__(self, *, decompress=False, **kwargs):
        """
        :param decompress:
            if true, will use ``hook_compressed``, for "transparently open compressed files".
            This is a shorter way of passing
        """
        if decompress:
            kwargs.setdefault('openhook', hook_compressed)
        self.kwargs = kwargs

    def get_fileinput(self, files):
        return _fileinput.input(files, **self.kwargs)

    @property
    def __argparse__(self):
        return dict(
            names=['infiles'],
            post_process=self.get_fileinput,
            metavar='INFILE',
        )


fileinput = FileInputType


def hook_compressed(filename, mode):
    """
    An alternative implemenation for ``fileinput.hook_compressed``, which partially
    works around Issue5758 ("fileinput.hook_compressed returning bytes from gz file").
    """
    ext = os.path.splitext(filename)[1]

    def fix_mode(mode):
        # default to text. from gzip.open docs:
        # The mode argument can be "r", "rb", "w", "wb", "x", "xb", "a" or "ab" for
        # binary mode, or "rt", "wt", "xt" or "at" for text mode. The default mode is
        # "rb".
        if mode in 'rwxa':
            return mode + 't'
        else:
            return mode

    if ext == '.gz':
        import gzip
        return gzip.open(filename, fix_mode(mode))
    elif ext == '.bz2':
        import bz2
        return bz2.BZ2File(filename, fix_mode(mode))
    else:
        return open(filename, mode)


################################################################################
