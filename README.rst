=========
ApeGears
=========

An improved ``ArgumentParser``, fully compatible with the standard ``argparse.ArgumentParser``.


What is ApeGears?
====================================

ApeGears' goal is making it easier to use the ``ArgumentParser``.
It provides simple and intuitive tools for achieving the most common use cases.

ApeGears defines an ``ArgumentParser`` which is a subclass of ``argparse.ArgumentParser``, and
is fully compatible with it.


What is wrong with ``argparse``?
---------------------------------

Nothing.  It works great.

However, it seems to be putting too much emphasis on being powerful, and too little on being intuitive.
For some actions, its interface is overly complicated.
The most common operations (e.g. defining flags and list arguments) are sometimes not perfectly intuitive.

Furthermore, it seems to be missing some useful options, such as support for ``dict`` arguments.
Also, using arguments of custom types (using the ``type`` parameter) doesn't work as smoothly as you'd hope.

Another annoyance is that when using ``FileType`` in write-mode, the output file is created very early (while
parsing cli args), not giving the option in your script to decide not to write to it after all.



Feaures
====================================

Following is an overview of the main features.  See below for more details on each.

- Intuitive "adder" methods for defining arguments: ``add_positional``, ``add_optional``, ``add_flag``, ``add_list``.

  - These cover the most common use cases.  You'd hardly ever need to use the basic ``add_argument`` method.

- Dict arguments, using ``add_dict`` method.
- Defining custom argument-types is simpler and more powerful, using "specs".
- Builtin support for some standard python types.

  - E.g. ``range``, ``date``, ``datetime``, ``Path``, literals, IP address, regular expression.

- An alternative ``FileType`` argument type, better than ``argparse.FileType``.
- Smooth integration with ``fileinput``.
- Builtin support for enum arguments.
- Builtin support for overriding log levels from cli, using `lo99ing <https://pypi.org/project/lo99ing/>`_.
- Can extract `description <https://docs.python.org/3/library/argparse.html#description>`_
  from docstring of caller module, to avoid doc duplication
  (enable by passing: ``description=CALLER_DOC``)
- Integration with other ``ArgumentParser``-related tools.

  - `argcomplete <https://pypi.org/project/argcomplete/>`_
  - `func_argparse <https://pypi.org/project/func-argparse/>`_


Avoiding ``argparse`` bugs:

- `Issue16399 <https://bugs.python.org/issue16399>`_ *append-with-nonempty-default*:
  apegears includes an easy-to-use workaround.
- `Issue13041 <https://bugs.python.org/issue13041>`_ *terminal width is not detected properly*:
  this is fixed in python 3.8, but using apegears avoids the issue for all version.


Adder methods
---------------------------------------

The standard all-in-one ``add_argument`` method is powerful, but not intuitive for some uses.
It has many kwargs, and not all combinations make sense.

Instead, in most cases, you can use the more precise and convenient adder methods:

- ``add_positional`` -- for defining positional arguments.
- ``add_optional`` -- for defining optional (i.e. non-positional) arguments.
- ``add_flag`` -- for defining (optional) flags ("switches").
- ``add_list`` -- for defining (optional) list arguments.

  - Multiple values can be passed in a single arg, or multiple.  The following are equivalent,
    and result with ``{'chars': ['a', 'b', 'c', 'd']}``::

        % prog.py --chars a b c d
        % prog.py --chars a b --chars c d
        % prog.py --chars a --chars b --chars c --chars d

You can still use the ``add_argument`` method for "advanced" argument definitions, but you'd rarely need to.


Dict arguments
----------------

Use ``add_dict`` for defining dict optional arguments.  E.g.::

    parser.add_dict('--overrides')
    parser.parse_args('--overrides log_level=debug logfile=out.log'.split()).overrides
    => OrderedDict([('log_level', 'debug'), ('logfile', 'out.log')])

Similar to list arguments, multiple key-value pairs can be passed in a single arg, or multiple.


Custom argument types
-------------------------

``argparse`` supports adding argument types by passing ``type=callable``, where ``callable``
converts the CLI string value to whatever you want (e.g. ``int`` converts the string to an integer).

This is not powerful enough, because often, when defining how a new argument type behaves, you'd want to include more
than just how to convert a CLI string.

ApeGears makes use of *Argument Type Specs*, which supports defining defaults for several fields:

- names
- default
- choices
- help
- metavar

Each of these can be explicitly overridden when calling the adder function.

Suppose you have a type ``T`` which you want to use with the parser, so you define
a spec for it, ``Tspec``.

For supporting usage like ``parser.add_xxx(..., type=T, ...)``, you either:

- register the spec: ``register_spec(T, Tspec)``
- define a class attribute named ``__argparse__``. E.g.: ``T.__argparse__ = Tspec``


Alternatively, this also works: ``parser.add_xxx(..., type=Tspec, ...)``


Argument types for standard python types
------------------------------------------

Argument type specs are predefined for some standard python types.
E.g., range, date, datetime, path, literals, IP address, regular expression.

Can be used like this::

    parser.add_optional(..., type='date', ...)  # also works: type=datetime.date
    parser.parse_args('--date 2020-03-04'.split()).date
    => datetime.date(2020, 3, 4)

Another example::

    parser.add_optional('indexes', ..., type='range', ...)  # also works: type=range
    parser.parse_args('--indexes 0:100:10'.split()).indexes
    => range(0, 100, 10)

Another example, for using literals (inspired by ``python-fire``):

    parser.add_optional('val', ..., type='literal', ...)
    parser.parse_args('--val {"four":4,"six":6}'.split()).val
    {'four': 4, 'six': 6}  # this is a dict


Improved ``FileType``
--------------------------

The problem with ``argparse.FileType``, is that in write-mode, the file is opened (created)
during cli-parsing, even in cases where you wouldn't want to write to the file.

For example, if your script is using ``argparse`` and takes a positional output file (``mode='w'``),
The following invocations will create an empty file named ``foo`` (deleting it if already exists)::

    % myscript.py foo -h  # will create the file, and print help message
    % myscript.py foo --no-such-option  # will create the file, and print argparse error message

There are other cases where you would decide not to write to output file (e.g. you fail generating
the content), but using ``argparse.FileType`` would still create an empty file (deleting existing
one).

The solution is using ``apegears.FileType`` instead, which lazily opens the file, when it is first
accessed.



``fileinput`` arguments
--------------------------

When you want to use `fileinput <https://docs.python.org/3/library/fileinput.html>`_ in
your script, ``apegears`` can save you a few lines of code::

    from apegears import ArgumentParser, fileinput
    parser = ArgumentParser()
    parser.add_positional(type=fileinput(decompress=True), nargs='*')
    args = parser.parse_args()
    for line in args.infiles:
        ...


Also, passing ``decompress=True`` handles compressed files better than using
``fileinput`` directly with ``hook_compressed``
(see `issue5758 <https://bugs.python.org/issue5758>`_).


Enum arguments
----------------

Enum types are also supported as argument types::

    class Direction(Enum):
        UP = 1
        DOWN = 2
        LEFT = 3
        RIGHT = 4

    parser.add_optional(type=Direction)
    parser.parse_args('--direction LEFT'.split()).direction
    => <Direction.LEFT: 3>


Overriding log levels from cli
--------------------------------

If you're using `lo99ing <https://pypi.org/project/lo99ing/>`_, the parser automatically
includes a -L/--log-level option for overriding log levels from cli.

E.g., to override from cli::

    myscript.py -L mylogger.traffic=debug yourlogger=error


The append-with-nonempty-default issue
------------------------------------------

You might have encountered a `bug <https://bugs.python.org/issue16399>`_ when using list arguments
in the standard ``ArgumentParser``::

    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('list', action='append', default=['D'])
    parser.parse_args('X'.split()).list
    => ['D', 'X']  # expected: ['X']

Basically, ``default``, instead of being used as a *default* value, is used as an *initial* value.

There is no easy-to-use workaround in the argparser level, but ApeGears provides one.

The ``add_list`` and ``add_dict`` methods include a workaround this issue.  It is enabled by default.

If you use the ``add_argument`` method directly, the workaround is disabled (for being compatible with ``argparse``),
but you can enable it by passing ``strict_default=True``.


Integration with other ``ArgumentParser``-related tools
===========================================================

argcomplete
---------------

`argcomplete <https://pypi.org/project/argcomplete/>`_ allows
"command line tab completion of arguments for your Python script".

For argcomplete users, there are a few (minor) advantages to using ApeGears ``ArgumentParser``, over ``argparse``'s:

- No need to call ``argcomplete.autocomplete(parser)``, it is called automatically for you
- Better completion of enum types
- Avoids the awkward way of setting a custom completer

  - use like: ``parser.add_argument(..., completer=MyCompleter)``
  - instead of: ``parser.add_argument(...).completer = MyCompleter``

- If you define custom argument types, you can also define a completer as part of their spec


func_argparse
---------------

`func_argparse <https://pypi.org/project/func-argparse/>`_ is used for
"Generating a nice command line interface for a list of functions or a module".

ApeGears lets you use func_argparse for generating an ApeGears ``ArgumentParser``, instead of ``argparse``'s.

The main advantages of using ``apegears + func_argparse`` over using ``func_argparse`` alone:

- Dict options
- Custom argument types, and argument types for standard python types

To use it, simply replace your import lines::

    import func_argparse            -->    import apegears.func_argparse
    from func_argparse import ...   -->    from apegears.func_argparse import ...



Getting Started
====================================

Installation
---------------

Using pip::

    pip install apegears


Start using the ``ArgumentParser``
-----------------------------------

``apegears.ArgumentParser`` is fully compatible with ``argparse``'s, so you can start
by replacing your import lines::

    import argparse            -->  import apegears
    from argparse import ...   -->  from apegears import ...

... to unleash the apes.


What does the Name Mean?
============================
Nothing. ::

    argparse = list('argparse')
    apegears = list('apegears')
    while argparse != apegears:
        random.shuffle(argparse)
    print('Got it?')
    print('Probably not...')
