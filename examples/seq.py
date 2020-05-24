""" A simple ``seq`` script, demonstrating range arg type. """

from apegears import ArgumentParser

if __name__ == '__main__':
    parser = ArgumentParser(description='print a sequence of numbers')
    parser.add_positional('seq', type=range)
    args = parser.parse_args()
    for i in args.seq:
        print(i)
