"""
Unit-tests for integration of the argparser with func_argparse generator.
"""

import unittest
import datetime
from enum import Enum
from typing import List, Dict, Union
from collections import OrderedDict

from apegears.func_argparse import func_argparser, make_single_main


################################################################################

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


class Enum1(Enum):
    foo = 1
    bar = 22
    coo = 333


################################################################################

class FuncArgparseTest(unittest.TestCase):
    """
    Tests integration with the func_argparse generator.
    """

    ################################################################################

    def test_basic(self):
        def foo(x: int, pretty: bool, z: float = 2.5):
            pass

        p = func_argparser(foo)

        def P(args):
            return p.parse_args(args.split())

        self.assertEqual(P('-x 7').x, 7)
        self.assertEqual(P('-x 7').z, 2.5)
        self.assertEqual(P('-x 7').pretty, False)
        self.assertEqual(P('-x 7 --pretty').pretty, True)
        self.assertEqual(P('-x 7 -p').pretty, True)
        self.assertEqual(P('-x 7 --no-pretty').pretty, False)
        self.assertEqual(P('-x 7 -z 9.5').z, 9.5)
        self.assertRaises(SystemExit, P, '')  # x is required
        self.assertRaises(SystemExit, P, '-x aaa')  # not an int value

    def test_list_and_enum(self):
        def foo(x: List[Enum1]):
            pass

        p = func_argparser(foo)

        def P(args):
            return p.parse_args(args.split())

        self.assertEqual(P('').x, [])
        self.assertEqual(P('-x bar coo').x, [Enum1.bar, Enum1.coo])
        self.assertEqual(P('-x bar -x coo').x, [Enum1.bar, Enum1.coo])
        self.assertRaises(SystemExit, P, '-x aaa')  # not an Enum1 value

    def test_dict_and_standard_type(self):
        def foo(x: Dict[int, datetime.date]):
            pass

        p = func_argparser(foo)

        def P(args):
            return p.parse_args(args.split())

        d1 = datetime.date(2001, 2, 3)
        d2 = datetime.date(2004, 5, 6)

        self.assertEqual(P('').x, OrderedDict())
        self.assertEqual(P('-x 1=%s 2=%s' % (d1, d2)).x, OrderedDict([(1, d1), (2, d2)]))
        self.assertEqual(P('-x 2=%s' % d2).x, OrderedDict([(2, d2)]))
        self.assertRaises(SystemExit, P, '-x qqq=%s' % d1)  # not an int key
        self.assertRaises(SystemExit, P, '-x 5=200')  # not a date value

    def test_custom_type(self):
        def foo(x: Type1 = None):
            pass

        p = func_argparser(foo)

        def P(args):
            return p.parse_args(args.split())

        self.assertEqual(P('').x, None)
        self.assertEqual(P('-x 4.5').x.val, 4.5)

    def test_union_with_none(self):
        def foo(x: Union[Type1, None]):
            pass

        p = func_argparser(foo)

        def P(args):
            return p.parse_args(args.split())

        self.assertEqual(P('').x, None)
        self.assertEqual(P('-x 4.5').x.val, 4.5)

    def test_main(self):

        def foo(x: int, pretty: bool, z: float = 2.5):
            return dict(locals())

        res = make_single_main(foo)('-x 5'.split())
        self.assertEqual(res, dict(x=5, pretty=False, z=2.5))
        res = make_single_main(foo)('-x 5 --pretty -z 3.5'.split())
        self.assertEqual(res, dict(x=5, pretty=True, z=3.5))


################################################################################
