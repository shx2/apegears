""" A simple ``copy`` script, demonstrating FileTypes. """

from apegears import ArgumentParser, FileType

if __name__ == '__main__':
    parser = ArgumentParser(description='copy a file')
    parser.add_positional('src', type=FileType('rb'))
    parser.add_positional('dest', type=FileType('wb'))
    args = parser.parse_args()

    # read:
    contents = args.src.read()

    # write:
    # NOTE: dest file is only created when writing to it (which is the point of this example):
    args.dest.write(contents)
