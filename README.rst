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


Why is it called "ApeGears"?
--------------------------------

::

    import random
    argparse = list('argparse')
    apegears = list('apegears')
    while argparse != apegears:
        random.shuffle(argparse)
    print('Got it?')

Probably not...



Feaures
====================================

Following is an overview of the main features.  See below for more details on each.

- Intuitive "adder" methods for defining arguments: ``add_positional``, ``add_optional``, ``add_flag``, ``add_list``.

  - These cover the most common use cases.  You'd hardly ever need to use the basic ``add_argument`` method.

- Dict arguments, using ``add_dict`` method.
- Defining custom argument-types is simpler and more powerful, using "specs".
- Argument-types for some standard python types are predefined and ready-to-use.

  - E.g. ``date``, ``datetime``, ``Path``, regular expression, IP address.

- Builtin support for enum arguments. E.g. ``parser.add_optional(type=MyEnum)``.
- Easy-to-use workaround append-with-nonempty-default issue. TBD add link.
- (PLANNED) Integration with other ``ArgumentParser``-related tools.


Adder methods
---------------------------------------

The standard all-in-one ``add_argument`` method is powerful, but not intuitive for some uses.
It has many kwargs, and not all combinations make sense.

Instead, in most cases, you can use the more precise and convenient adder methods:

- ``add_positional`` -- for defining positional arguments
- ``add_optional`` -- for defining optional (i.e. non-positional) arguments
- ``add_flag`` -- for defining (optional) flags ("switches")
- ``add_list`` -- for defining (optional) list arguments

  - Multiple values can be passed in a single arg, or multiple.  The following are equivalent,
    and result with ``{'chars': ['a', 'b', 'c', 'd']}``::

        % prog.py --chars a b c d
        % prog.py --chars a b --chars c d
        % prog.py --chars a --chars b --chars c --chars d

You can still use the ``add_argument`` method for "advanced" argument definitions, but you'd rarely need to.


Dict arguments
----------------
TBD


Custom argument types
-------------------------
TBD


Argument types for standard python types
------------------------------------------
TBD


Enum arguments
----------------
TBD


The append-with-nonempty-default issue
------------------------------------------
TBD


Integration with other ``ArgumentParser``-related tools
------------------------------------------------------------
To come...



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

which unleashes the apes.


