#! /usr/bin/env python
"""
Creates an ArgumentParser with a single argument defined by CLI arguments,
and parses the rest of CLI arguments using that parser.

Useful for quick testing of ArgumentParser.

For example::

    % meta_parsrer.py LIST dates --type date --required -- --dates 2020-03-03 2022-04-08
    dates = [datetime.date(2020, 3, 3), datetime.date(2022, 4, 8)]

Another example, for testing the strict_default flag:

    # Using argparse, demostrating issue16399:
    % meta_parsrer.py ARGUMENT --foo --action append --default "['aa', 'bb']" -- --foo cc
    foo = ['aa', 'bb', 'cc']

    # List option with strict_default disabled reproduces the problem:
    % meta_parsrer.py LIST foo --default "['aa', 'bb']" --no-strict-default -- --foo cc
    foo = ['aa', 'bb', 'cc']

    # List option by default avoid the problem:
    % meta_parsrer.py LIST foo --default "['aa', 'bb']" -- --foo cc
    foo = ['cc']

"""

from apegears import ArgumentParser, CALLER_DOC, REMAINDER
import builtins
import enum


###############################################################################

EMPTY = object()


class ArgForm(enum.Enum):
    POSITIONAL = 1
    OPTIONAL = 2
    FLAG = 3
    LIST = 4
    DICT = 5
    ARGUMENT = 99


class Action(enum.Enum):
    store = 'store'
    store_const = 'store_const'
    store_true = 'store_true'
    store_false = 'store_false'
    append = 'append'
    append_const = 'append_const'
    count = 'count'


def nargs_type(x):
    # convert nargs string value to a nargs param
    if x in ['*', '+', '?', REMAINDER]:
        return x
    try:
        return int(x)
    except ValueError:
        pass
    raise ValueError(x)


###############################################################################

def get_meta_args():
    parser = ArgumentParser(description=CALLER_DOC, argument_default=EMPTY)

    parser.add_positional('argform', type=ArgForm)
    parser.add_positional('argname')

    parser.add_optional('nargs', type=nargs_type)
    parser.add_optional('default', type='literal')
    parser.add_optional('type', type=lambda s: getattr(builtins, s, s))
    parser.add_optional('arghelp', dest='help', help='the "help" param')
    parser.add_optional('metavar')
    parser.add_optional('dest')
    parser.add_optional('action', type=Action)
    parser.add_optional('const', type='literal')
    parser.add_flag('required')
    parser.add_flag('strict-default')

    args, rest = parser.parse_known_args()

    if rest and rest[0] == '--':
        rest = rest[1:]
    return args, rest


def create_argparser(meta_args):
    parser = ArgumentParser(description='ArgumentParser created from meta-CLI')

    kwargs = {k: v for k, v in vars(meta_args).items() if v != EMPTY}
    argname = kwargs.pop('argname')
    argform = kwargs.pop('argform')
    if 'action' in kwargs:
        kwargs['action'] = kwargs['action'].value

    adder = getattr(parser, 'add_%s' % argform.name.lower())
    print('# %s %r' % (adder.__name__, kwargs))
    adder(argname, **kwargs)

    return parser


###############################################################################
# MAIN

def main():
    meta_args, rest = get_meta_args()

    parser = create_argparser(meta_args)

    args = parser.parse_args(rest)

    print('# ARGS:  %r' % rest)
    for k, v in vars(args).items():
        print('%s = %r' % (k, v))


###############################################################################

if __name__ == '__main__':
    main()
