"""
Unit-tests for the ArgumentParser.add_xxx() methods.
"""

import unittest

from apegears import ArgumentParser as AP


################################################################################

class AddArgumentTest(unittest.TestCase):
    """
    Tests the basic functionality of the add_xxx() methods.
    """

    ################################################################################

    def test_positional(self):
        def P(*a, **kw):
            return self._parse('positional', *a, **kw)

        self.assertEqual(P('arg1', cli_args='abc').arg1, 'abc')
        self.assertEqual(P(dest='arg1', cli_args='abc').arg1, 'abc')

        # test type and default:
        self.assertEqual(P('arg1', type=float, cli_args='5.5').arg1, 5.5)
        self.assertEqual(P('arg1', type=float, default='1.5', cli_args='5.5').arg1, 5.5)
        self.assertEqual(P('arg1', type=float, default='1.5', cli_args='').arg1, 1.5)

        # raise if action or required are passed
        self.assertRaises(ValueError, P, 'arg1', required=True)
        self.assertRaises(ValueError, P, 'arg1', action='store')
        # raise if not providing neither name nor dest
        self.assertRaises((ValueError, TypeError), P)
        # raise if providing both name and dest
        self.assertRaises(ValueError, P, 'argXXX', dest='arg1')

    def test_positional_list(self):
        def P(*a, **kw):
            return self._parse('positional', *a, **kw)

        self.assertEqual(P('arg1', nargs='*', type=int, cli_args='').arg1, [])
        self.assertEqual(P('arg1', nargs='*', type=int, cli_args='5 6 7', ).arg1, [5, 6, 7])
        self.assertEqual(P('arg1', nargs='+', type=int, cli_args='5 6 7',).arg1, [5, 6, 7])
        self.assertEqual(P('arg1', nargs=3, type=int, cli_args='5 6 7', ).arg1, [5, 6, 7])

        # raise if not passed and nargs='+'
        self.assertRaises(SystemExit, P, 'arg1', nargs='+', cli_args='')
        # raise if passed a wrong number of args
        self.assertRaises(SystemExit, P, 'arg1', nargs=2, cli_args='1')
        self.assertRaises(SystemExit, P, 'arg1', nargs=2, cli_args='1 2 3')

    def test_optional(self):
        def P(*a, **kw):
            return self._parse('optional', *a, **kw)

        # test different names:
        for req in [None, False, True]:
            self.assertEqual(P('x', required=req, cli_args='-x y').x, 'y')
            self.assertEqual(P('xx', required=req, cli_args='--xx y').xx, 'y')
            self.assertEqual(P('x', 'xx', required=req, cli_args='--xx y').xx, 'y')
            self.assertEqual(P('x', 'xx', required=req, cli_args='-x y').xx, 'y')
            self.assertEqual(P('-x', required=req, cli_args='-x y').x, 'y')
            self.assertEqual(P('--xx', required=req, cli_args='--xx y').xx, 'y')
            self.assertEqual(P('-x', '--xx', required=req, cli_args='--xx y').xx, 'y')
            self.assertEqual(P('-x', '--xx', required=req, cli_args='-x y').xx, 'y')

        # test type and default
        self.assertEqual(P('x', type=float, cli_args='-x 3.25').x, 3.25)
        self.assertEqual(P('x', type=float, default='7.75', cli_args='-x 3.25').x, 3.25)
        self.assertEqual(P('x', type=float, default='7.75', cli_args='').x, 7.75)

        # raise if name not passed
        self.assertRaises(ValueError, P)
        # raise if required not passed
        self.assertRaises(SystemExit, P, 'x', required=True, cli_args='')

    def test_flag(self):
        def P(*a, **kw):
            return self._parse('flag', *a, **kw)

        self.assertEqual(P('x', cli_args='-x').x, True)
        self.assertEqual(P('-x', cli_args='-x').x, True)
        self.assertEqual(P('x', 'xx', cli_args='-x').xx, True)
        self.assertEqual(P('x', 'xx', cli_args='--xx').xx, True)
        self.assertEqual(P('--xx', cli_args='--xx').xx, True)
        self.assertEqual(P('-x', '--xx', cli_args='-x').xx, True)
        self.assertEqual(P('-x', '--xx', cli_args='--xx').xx, True)
        self.assertEqual(P('x', cli_args='').x, False)

        # raise if irrelevant args are passed
        for k in ['action', 'nargs', 'required', 'const', 'default', 'type', 'choices']:
            self.assertRaises(ValueError, P, **{k: None})

    def test_list(self):
        def P(*a, **kw):
            return self._parse('list', *a, **kw)

        self.assertEqual(P('x', cli_args='').x, [])
        self.assertEqual(P('-x', cli_args='-x aa').x, ['aa'])
        self.assertEqual(P('x', cli_args='-x aa bb').x, ['aa', 'bb'])
        self.assertEqual(P('x', cli_args='-x aa bb -x cc').x, ['aa', 'bb', 'cc'])
        self.assertEqual(P('x', type=int, cli_args='-x -222 666').x, [-222, 666])
        self.assertEqual(P('x', type=int, cli_args='-x -2 4 -x 6 8 10').x, [-2, 4, 6, 8, 10])

        # raise if action is passed
        self.assertRaises(ValueError, P, 'arg1', action='store')
        # raise if nargs='?' is passed
        self.assertRaises(ValueError, P, 'arg1', nargs='?')

    def test_list_nonempty_default_value(self):
        def P(*a, **kw):
            return self._parse('list', *a, **kw)

        d = ['a', 'b']
        self.assertEqual(P('-x', default=d, cli_args='').x, d)
        # test the workaround this issue: https://bugs.python.org/issue16399
        self.assertEqual(P('-x', default=d, cli_args='-x c').x, ['c'])

    def test_dict(self):
        def P(*a, **kw):
            return self._parse('dict', *a, **kw)

        self.assertEqual(P('x', cli_args='').x, {})
        self.assertEqual(P('-x', cli_args='-x aa=bb').x, {'aa': 'bb'})
        self.assertEqual(P('x', cli_args='-x aa=bb').x, {'aa': 'bb'})
        self.assertEqual(P('x', type=int, cli_args='-x aa=1 bb=2 -x cc=3').x,
                         {'aa': 1, 'bb': 2, 'cc': 3})
        self.assertEqual(P('x', key_type=int, type=float, cli_args='-x 1=1.5 2=2.5 -x 3=3.5').x,
                         {1: 1.5, 2: 2.5, 3: 3.5})

        # raise if action is passed
        self.assertRaises(ValueError, P, 'arg1', action='store')
        # raise if nargs='?' is passed
        self.assertRaises(ValueError, P, 'arg1', nargs='?')

    def test_dict_nonempty_default_value(self):
        def P(*a, **kw):
            return self._parse('dict', *a, **kw)

        d = {'a': 'aa', 'b': 'bb'}
        self.assertEqual(P('-x', default=d, cli_args='').x, d)

        # test the workaround this issue: https://bugs.python.org/issue16399
        self.assertEqual(P('-x', default=d, cli_args='-x c=cc').x, {'c': 'cc'})

    def test_issue16399(self):
        # for compatibility, we make sure we reproduce the old behavior, see
        # https://bugs.python.org/issue16399
        self.assertEqual(
            self._parse(
                'argument', '-x', action='append', default=['aa', 'bb'],
                cli_args='-x cc',
            ).x,
            ['aa', 'bb', 'cc'],
        )

    ################################################################################

    def _parse(self, arg_type, *args, cli_args=None, **kwargs):
        ap = AP()
        add_func = getattr(ap, 'add_' + arg_type)
        add_func(*args, **kwargs)
        if cli_args is not None:
            return ap.parse_args(cli_args.split())


################################################################################
