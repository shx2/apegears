"""
Unit-tests for integration of custom types with the argparser.
"""

import unittest
from enum import Enum

from apegears import ArgumentParser as AP, register_spec


################################################################################
# TypeMinimal -- with a minimal spec

class TypeMinimal:
    def __init__(self, val):
        self.val = val


TypeMinimal.__argparse__ = dict(from_string=TypeMinimal)


################################################################################
# Type1 -- defines its own spec

class Type1:

    def __init__(self, val):
        self.val = val

    @classmethod
    def from_string(cls, x):
        return cls(float(x))


Type1.__argparse__ = dict(
    from_string=Type1.from_string,
    default='-1',
    names=['type1', 't'],
    help='a Type1 object',
)


################################################################################
# Type2 -- registered spec

class Type2:

    def __init__(self, val):
        self.val = val

    @classmethod
    def from_string(cls, x):
        return cls(float(x))


register_spec(
    Type2,
    dict(
        from_string=Type2.from_string,
        default='-1',
        names=['type2', 'T'],
        help='a Type2 object',
    )
)


################################################################################
# Enum type -- auto generated spec

class Enum1(Enum):
    foo = 1
    bar = 22
    coo = 333


################################################################################

class TypeIntegrationTest(unittest.TestCase):
    """
    Tests integration of custom types as cli arguments.
    """

    ################################################################################

    def test_fields(self):
        def P(*a, **kw):
            return self._parse('optional', *a, **kw)

        # most basic
        self.assertEqual(P('x', type=TypeMinimal, cli_args='-x aa').x.val, 'aa')

        # test names -- when not defined in spec:
        self.assertEqual(P('x', type=TypeMinimal, cli_args='-x aa').x.val, 'aa')
        self.assertRaises(ValueError, P, type=TypeMinimal)
        # test names -- when defined in spec:
        self.assertEqual(P(type=Type1, cli_args='').type1.val, -1)
        self.assertEqual(P(type=Type1, cli_args='--type1 2').type1.val, 2)
        self.assertEqual(P(type=Type1, cli_args='-t 2').type1.val, 2)
        self.assertEqual(P('x', type=Type1, cli_args='').x.val, -1)
        self.assertEqual(P('x', type=Type1, cli_args='-x 2').x.val, 2)
        self.assertEqual(P(type=Type2, cli_args='').type2.val, -1)
        self.assertEqual(P(type=Type2, cli_args='--type2 2').type2.val, 2)
        self.assertEqual(P(type=Type2, cli_args='-T 2').type2.val, 2)
        self.assertEqual(P('x', type=Type2, cli_args='').x.val, -1)
        self.assertEqual(P('x', type=Type2, cli_args='-x 2').x.val, 2)

        # test default values -- when not defined in spec, and not required:
        self.assertEqual(P('x', type=TypeMinimal, cli_args='').x, None)
        self.assertEqual(P('x', type=TypeMinimal, default='zz', cli_args='').x.val, 'zz')
        # test default values -- when defined in spec:
        for T in [Type1, Type2]:
            self.assertEqual(P('x', type=T, cli_args='').x.val, -1)
            self.assertEqual(P('x', type=T, default='-5', cli_args='').x.val, -5)

    def test_list(self):
        def P(*a, **kw):
            return self._parse('list', *a, **kw)

        # default is always the empty collection, regardless of spec
        for T in [TypeMinimal, Type1, Type2]:
            self.assertEqual(P('x', type=T, cli_args='').x, [])
            self.assertEqual(P('x', type=T, cli_args='-x').x, [])

        res = P('x', type=TypeMinimal, cli_args='-x aa').x
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].val, 'aa')
        for T in [Type1, Type2]:
            res = P('x', type=T, cli_args='-x 7.5 8.5 -x 9.5').x
            self.assertEqual(len(res), 3)
            self.assertEqual([y.val for y in res], [7.5, 8.5, 9.5])

    def test_dict(self):
        def P(*a, **kw):
            return self._parse('dict', *a, **kw)

        # default is always the empty collection, regardless of spec
        for T in [TypeMinimal, Type1, Type2]:
            self.assertEqual(P('x', type=T, cli_args='').x, {})
            self.assertEqual(P('x', type=T, cli_args='-x').x, {})

        res = P('x', type=TypeMinimal, cli_args='-x aa=bb').x
        self.assertEqual(len(res), 1)
        self.assertEqual(list(res.keys())[0], 'aa')
        self.assertEqual(list(res.values())[0].val, 'bb')
        for T in [Type1, Type2]:
            res = P('x', type=T, key_type=int, cli_args='-x 7=7.5 8=8.5 -x 9=9.5').x
            self.assertEqual(len(res), 3)
            self.assertEqual(list(res.keys()), [7, 8, 9])
            self.assertEqual([y.val for y in res.values()], [7.5, 8.5, 9.5])

    def test_enum(self):
        def P(*a, **kw):
            return self._parse('optional', *a, **kw)

        self.assertEqual(P('x', type=Enum1, cli_args='').x, None)
        self.assertEqual(P('x', type=Enum1, default=Enum1.coo, cli_args='').x, Enum1.coo)
        self.assertEqual(P('x', type=Enum1, cli_args='-x foo').x, Enum1.foo)
        self.assertEqual(P('x', type=Enum1, default=Enum1.coo, cli_args='-x bar').x, Enum1.bar)
        self.assertRaises(SystemExit, P, 'x', type=Enum1, cli_args='-x no-such-value')

        # test choices can be passed explicitly:
        choices = [Enum1.foo, Enum1.bar]
        self.assertEqual(P('x', type=Enum1, choices=choices, cli_args='').x, None)
        self.assertEqual(P('x', type=Enum1, choices=choices, cli_args='-x bar').x, Enum1.bar)
        self.assertRaises(SystemExit, P, 'x', type=Enum1, choices=choices, cli_args='-x coo')

    def test_enum_list(self):
        def P(*a, **kw):
            return self._parse('list', *a, **kw)

        two_vals = [Enum1.foo, Enum1.bar]
        self.assertEqual(P('x', type=Enum1, cli_args='').x, [])
        self.assertEqual(P('x', type=Enum1, cli_args='-x foo bar').x, two_vals)
        self.assertEqual(P('x', type=Enum1, cli_args='-x foo -x bar').x, two_vals)
        self.assertRaises(SystemExit, P, 'x', type=Enum1, choices=two_vals, cli_args='-x coo')
        self.assertRaises(SystemExit, P, 'x', type=Enum1, cli_args='-x no-such-value')

    def test_enum_dict(self):
        def P(*a, **kw):
            return self._parse('dict', *a, **kw)

        self.assertEqual(P('x', type=Enum1, cli_args='').x, {})
        self.assertEqual(P('x', type=Enum1, cli_args='-x k1=foo k2=bar').x,
                         {'k1': Enum1.foo, 'k2': Enum1.bar})
        self.assertEqual(P('x', type=Enum1, cli_args='-x k1=foo -x k2=bar').x,
                         {'k1': Enum1.foo, 'k2': Enum1.bar})
        self.assertRaises(SystemExit, P, 'x', type=Enum1, cli_args='-x k1=no-such-value')
        # note: dict with choices is not supported

    ################################################################################

    def _parse(self, arg_type, *args, cli_args=None, **kwargs):
        ap = AP()
        add_func = getattr(ap, 'add_' + arg_type)
        add_func(*args, **kwargs)
        if cli_args is not None:
            return ap.parse_args(cli_args.split())


################################################################################
