#! /usr/bin/env python3
"""
TBD
"""

import inspect
import apegears


def foo(aa, bb: float = 5.5, *, cc: int, dd='bar'):
    """
    Perform some serious fooing.
    """
    sig = inspect.Signature.from_callable(foo)
    print('%s%s:' % (foo.__name__, sig))
    for p in sig.parameters:
        print('  %s = %r' % (p, locals()[p]))


if __name__ == '__main__':
    apegears.main(foo)
