"""
Argument-type specs.
"""

from enum import Enum


################################################################################

_SPEC_REGISTRY = {}


################################################################################

class ArgParseSpec:
    """
    A class defining *type* default behavior of argument-parser args ("action fields")
    for argument *types*.

    ``from_string`` corresponds to the argparse ``type`` field. It is a callable which defines
    how to convert a string value (read from CLI) to an object of that type.
    """

    EMPTY = object()

    def __init__(self,
                 names=EMPTY, default=EMPTY, from_string=None, post_process=EMPTY,
                 choices=EMPTY, help=EMPTY, metavar=EMPTY, completer=EMPTY):
        self.names = names
        self.default = default
        self.from_string = from_string
        self.post_process = post_process
        self.choices = choices
        self.help = help
        self.metavar = metavar
        self.completer = completer

    @property
    def __argparse__(self):
        return self


def find_spec(cls):
    # first try the registy
    try:
        return _SPEC_REGISTRY[cls]
    except KeyError:
        pass
    # look for __argparse__ attribute:
    spec = getattr(cls, '__argparse__', None)
    if spec is not None:
        return to_spec(spec)
    # we can generate sensible specs for some types on the fly:
    spec = gen_type_spec(cls)
    if spec is not None:
        return to_spec(spec)
    return None


def register_spec(cls, spec):
    """
    Register an arg-type spec.  Once registered, ``cls`` can be used as the ``type`` argument
    of the ``parser.add_xxx`` methods, e.g. ``parser.add_optional(..., type=cls, ...)``.
    """
    spec = to_spec(spec)
    _SPEC_REGISTRY[cls] = spec
    return spec


def to_spec(spec):
    if isinstance(spec, ArgParseSpec):
        return spec
    if isinstance(spec, type):
        attr_dict = {k: v for k, v in spec.__dict__.items() if not k.startswith('_')}
    else:
        attr_dict = dict(spec)
    return ArgParseSpec(**attr_dict)


def gen_type_spec(cls, **kwargs):
    """
    Auto-generate spec for some supported types, e.g. Enums.
    """
    if isinstance(cls, type) and issubclass(cls, Enum):
        return gen_enum_spec(cls, **kwargs)
    return None


################################################################################
# enum support

class _EnumValueType:

    def __init__(self, enum_cls):
        self.enum_cls = enum_cls

    def __call__(self, key):
        # converts a value from cli to an enum member
        try:
            return self.enum_cls[key]
        except KeyError:
            raise ValueError(key) from None

    @property
    def __name__(self):
        # defiend for nicer error messages
        return self.enum_cls.__name__

    @property
    def __metavar__(self):
        return self.__name__.upper()


def gen_enum_spec(cls, **kwargs):
    enum_value_type = _EnumValueType(cls)
    strings = [e.name for e in cls]
    kw = dict(
        names=[enum_value_type.__name__.lower()],
        from_string=enum_value_type,
        choices=list(cls),
        help='/'.join(strings),
        completer=lambda *a, **kw: strings,
    )
    kw.update(kwargs)
    return ArgParseSpec(**kw)


################################################################################
