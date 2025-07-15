#!/usr/bin/env python3

import argparse
import ext4

def list_files(fs, basename, inode_id):
    for entry in fs.files(inode_id):
        if entry.name in ['.', '..']:
            continue
        if entry.type == 1:
            inode = fs.lookup(entry.inode_id)
        elif entry.type == 2:
            list_files(fs, f'{basename}{entry.name}/', entry.inode_id)


def do_list(filename, args):
    with open(filename, 'rb') as f:
        fs = ext4.FileSystem(f)
        list_files(fs, '/', 2)

        id = fs.find('/foo/bar/bar.txt')
        print(id)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str)
    parser.add_argument("paths", type=str, nargs='*', default=['/'])
    args = parser.parse_args()
    do_list(args.filename, args.paths)

if __name__ == '__main__':
    main()
