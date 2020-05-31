0.2.1
-----
* Support for new arg types: ``log level``, ``literal``.
* New adder methods: add_positional_list
* Support extracting description from docstring of caller module
* Workaround Issue13041: terminal width is not detected properly

0.2.0
-----
* Support for new arg types: ``range``, ``fileinput``.
* An alternative ``FileType`` implementaion, better than ``argparse``'s.
* Integration with ``argcomplete``.
* Integration with ``func_argparse`` (currently broken).
* Added samples scripts, to demonstrate some features.

0.1.0
-----
* Adder methods: add_positional, add_optional, add_flag, add_list.
* Dict arguments.
* Custom argument-types using "specs".
* Support for some standard python types.
* Support for enum arguments.
* Workaround append-with-nonempty-default bug.

Future/Planned
----------------
* Integration with ``autocommand``
