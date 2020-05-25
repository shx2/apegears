"""
Tools for defining arguments involving reading and writing files.
"""

import os
import os.path
import argparse as _ap
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
# FileType

class LazyOpenFile:
    """
    Lzay-open functionality.  Can be used instead of builtin ``open`` function.

    Upon calling ``LazyOpenFile(...)``, it checks the file can be opened, but
    doesn't actually open it (in read mode, it might be opened and closed immediately).

    The file is only opened on first access.  In write mode, it means the file is not created
    until/unless being accessed.
    """

    def __init__(self, file, mode='r', *args, **kwargs):
        self.__dict__.update(
            _file=file,
            _mode=mode,
            _args=args,
            _kwargs=kwargs,
            _f=None,
        )
        self._check()

    def __getattr__(self, attr, *args):
        if attr in self.__dict__:
            return super().__getattr__(attr, *args)
        else:
            self._open()
            return getattr(self._f, attr, *args)

    def __setattr__(self, attr, *args):
        if attr in self.__dict__:
            return super().__setattr__(attr, *args)
        else:
            self._open()
            return setattr(self._f, attr, *args)

    def _open(self):
        if self._f is None:
            self._f = self._raw_open()

    def _raw_open(self):
        return open(self._file, self._mode, *self._args, **self._kwargs)

    def _check(self):
        mode = self._mode[0]
        f = self._file
        if mode == 'r':
            # read mode, open and close, and raise if fails:
            with self._raw_open():
                pass
        else:
            # write mode
            if (not _is_writeable(f)) or (mode == 'x' and os.path.exists(f)):
                # not writeable
                self._raw_open()  # should raise
                assert 0, 'should have raised already'

    def __repr__(self):
        return '<%s %r %r>' % (type(self).__name__, self._flle, self._mode)


class FileType(_ap.FileType):
    """
    Same as ``argparse.FileType``, but in write-mode (w/a/x), the file
    is opened lazily, to avoid creating a file before we actually need to.

    The lazy functionality is implementeed in ``LazyOpenFile``.
    """

    def __call__(self, string):
        is_write = self._mode and self._mode[0] in 'wax'
        if string == '-' or not is_write:
            return super().__call__(string)

        # all other arguments are used as file names
        try:
            return LazyOpenFile(string, self._mode, self._bufsize, self._encoding, self._errors)
        except OSError as e:
            message = _ap._("can't open '%s': %s")
            raise _ap.ArgumentTypeError(message % (string, e))


def _is_writeable(fnm):
    """
    Copied from:
    https://www.novixys.com/blog/python-check-file-can-read-write/#2_Check_if_File_can_be_Read
    """
    if os.path.exists(fnm):
        # path exists
        if os.path.isfile(fnm):  # is it a file or a dir?
            # also works when file is a link and the target is writable
            return os.access(fnm, os.W_OK)
        else:
            return False  # path is a dir, so cannot write as a file
    # target does not exist, check perms on parent dir
    pdir = os.path.dirname(fnm)
    if not pdir:
            pdir = '.'
    # target is creatable if parent dir is writable
    return os.access(pdir, os.W_OK)


################################################################################
