#!/usr/bin/env python3

import argparse
import ext4

def is_match(name, candidates):
    if len(candidates) == 0:
        return True
    for candidate in candidates:
        if candidate in name:
            return True
    return False

def list_files(fs, basename, inode_id, paths):
    for entry in fs.files(inode_id):
        if entry.name in ['.', '..']:
            continue
        full_name = f'{basename}{entry.name}'
        if is_match(full_name, paths):
            print(f'{full_name}')
        if entry.type == ext4.DIRENT_DIR:
            list_files(fs, f'{basename}{entry.name}/', entry.inode_id, paths)


def do_list(filename, paths):
    with open(filename, 'rb') as f:
        fs = ext4.FileSystem(f)
        list_files(fs, '/', ext4.ROOT, paths)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str)
    parser.add_argument("paths", type=str, nargs='*', default=['/'])
    args = parser.parse_args()
    do_list(args.filename, args.paths)

if __name__ == '__main__':
    main()
