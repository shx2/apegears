"""
Print data stored in a pickle file (optionally compressed).

This simple script demonstrating `pickled_data` arg type.
"""

from apegears import ArgumentParser, CALLER_DOC

if __name__ == '__main__':
    parser = ArgumentParser(description=CALLER_DOC)
    parser.add_positional('data', type='pickled_data')
    args = parser.parse_args()
    print(args.data)
