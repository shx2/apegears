"""
Print a sequence of numbers.

This is a simple ``seq`` script, demonstrating range arg type.
"""

from apegears import ArgumentParser, CALLER_DOC

if __name__ == '__main__':
    parser = ArgumentParser(description=CALLER_DOC)
    parser.add_positional('seq', type=range)
    args = parser.parse_args()
    for i in args.seq:
        print(i)
