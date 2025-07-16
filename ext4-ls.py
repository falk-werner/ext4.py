#!/usr/bin/env python3

import argparse
import ext4

def get_filetype(inode):
    if inode.is_reg():
        return 'r'
    elif inode.is_dir():
        return 'd'
    elif inode.is_symlink():
        return 'l'
    elif inode.is_socket():
        return 's'
    elif inode.is_fifo():
        return 'f'
    elif inode.is_char():
        return 'c'
    elif inode.is_block():
        return 'b'
    else:
        return '?'


def do_list(filename, paths):
    with open(filename, 'rb') as f:
        fs = ext4.FileSystem(f)
        for path in paths:
            id = fs.find(path)
            if id is not None:
                inode = fs.lookup(id)
                if inode.is_dir():
                    print(f'{path}')
                    for entry in fs.files(id):
                        inode2 = fs.lookup(entry.inode_id)
                        filetype = get_filetype(inode2)
                        print(f'  {filetype} {inode2.size:<10} {entry.name}')
                else:
                    filetype = get_filetype(inode)
                    print(f'{filetype} {inode.size:<10} {path}')
                print()
            else:
                print(f'not found: {path}')



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str)
    parser.add_argument("paths", type=str, nargs='*', default=['/'])
    args = parser.parse_args()
    do_list(args.filename, args.paths)

if __name__ == '__main__':
    main()
