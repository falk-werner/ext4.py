#!/usr/bin/env python3

import argparse
import ext4

def do_list(filename, paths):
    with open(filename, 'rb') as f:
        fs = ext4.FileSystem(f)
        for path in paths:
            id = fs.find(path)
            inode = fs.lookup(id)

            print(f'{path}')
            print(f'size: {inode.size}')
            print()



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str)
    parser.add_argument("paths", type=str, nargs='*', default=['/'])
    args = parser.parse_args()
    do_list(args.filename, args.paths)

if __name__ == '__main__':
    main()
