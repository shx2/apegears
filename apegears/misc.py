"""
Private definitions of actions, types, etc. used in this pacakge.
"""

import argparse as _ap
import copy as _copy


################################################################################
# custom actions

class _ExtendAction(_ap.Action):
    """
    Definition of an "extend" action, similar idea to "append" action.
    """

    def __init__(self, nargs=None, **kwargs):
        if nargs == 0:
            raise ValueError('nargs for extend actions must be > 0')
        if 'const' in kwargs:
            raise ValueError('const= does not apply to extend actions')
        super().__init__(nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        items = _copy.copy(_ensure_value(namespace, self.dest, []))
        items.extend(values)
        setattr(namespace, self.dest, items)


class _SetItemAction(_ap.Action):
    """
    Definition of a "set-items" action, for adding key-value pairs to the
    destination dict.
    """

    def __init__(self, nargs=None, key_type=str, **kwargs):
        if nargs == 0:
            raise ValueError('nargs for setitem actions must be > 0')
        if 'const' in kwargs:
            raise ValueError('const= does not apply to setitem actions')
        super().__init__(nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        items = _copy.copy(_ensure_value(namespace, self.dest, {}))
        # values is a list of (key, value) pairs
        items.update(values)
        setattr(namespace, self.dest, items)


################################################################################
# custom types

class _KeyValueType:
    """
    Definition of a key-value type, whose value represents an item in a dict.
    Used by dict-options (``ArgumentParser.add_dict``).
    """

    def __init__(self,
                 key_type=None, value_type=None, *,
                 delim='=', key_metavar=None, value_metavar=None):
        self.key_type = key_type
        self.key_metavar = key_metavar
        self.value_type = value_type
        self.value_metavar = value_metavar
        self.delim = delim

        for t in [self.key_type, self.value_type]:
            if t is not None and not callable(t):
                raise ValueError('%r is not callable' % t)

    def get_metavar(self):
        key_mv = self.key_metavar
        if key_mv is None:
            key_mv = self._type_metavar(self.key_type, 'KEY')
        value_mv = self.value_metavar
        if value_mv is None:
            value_mv = self._type_metavar(self.value_type, 'VALUE')
        return '%s%s%s' % (key_mv, self.delim, value_mv)

    def __call__(self, arg_string):
        key, delim, value = arg_string.partition(self.delim)
        if not delim:
            raise ValueError('invalid key=value string: %r' % arg_string)
        if self.key_type is not None:
            key = self.key_type(key)
        if self.value_type is not None:
            value = self.value_type(value)
        return (key, value)

    def __repr__(self):
        # defiend for nicer error messages
        return '%s=%s' % (
            self._type_metavar(self.key_type, 'KEY'),
            self._type_metavar(self.value_type, 'VALUE'),
        )

    def _type_metavar(self, t, default=None):
        if t is None:
            return default
        return '%s' % getattr(t, '__name__', t)


def _ensure_value(namespace, name, value):
    if getattr(namespace, name, None) is None:
        setattr(namespace, name, value)
    return getattr(namespace, name)


################################################################################
# workaround append-with-nonempty-default issue (https://bugs.python.org/issue16399):

class _StrictDefaultActionWrapper(_ap.Action):
    """
    An Action class which wraps another action object (which modifies a collection,
    e.g. action='append', 'extend', 'setitem'), and changes its behavior in case of a
    non-empty default value.

    E.g. for ``action='append'``, with ``default=['foo']``, if a value of 'bar' is provided,
    the resulting list is ``['bar']`` instead of ``['foo', 'bar']``.

    See https://bugs.python.org/issue16399 .
    """

    def __init__(self, action, empty_value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.action = action
        self.empty_value = empty_value
        self._called = False

    def __call__(self, parser, namespace, *args, **kwargs):
        self._wipe_default(namespace)
        return self.action.__call__(parser, namespace, *args, **kwargs)

    def _wipe_default(self, namespace):
        if self._called:
            return
        self._called = True
        cur_value = getattr(namespace, self.dest, object())
        if cur_value != self.default:
            return
        # wipe it
        setattr(namespace, self.dest, _copy.copy(self.empty_value))

    def _get_kwargs(self):
        return self.action._get_kwargs()

    def _get_args(self):
        return self.action._get_args()

    def __repr__(self):
        return self.action.__repr__()


################################################################################
