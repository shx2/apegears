""" A simple ``cat`` script, demonstrating fileinput arg type. """

from apegears import ArgumentParser, fileinput

if __name__ == '__main__':
    parser = ArgumentParser(description='cat - concatenate files and print on the standard output')
    parser.add_positional(type=fileinput(decompress=True), nargs='*')
    args = parser.parse_args()
    for line in args.infiles:
        print(line, end='')
