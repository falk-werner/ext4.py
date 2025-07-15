#!/usr/bin/env python3

import argparse
import ext4

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
                        print(f'  {inode2.size:<10} {entry.name}')
                else:
                    print(f'{inode.size:<10} {path}')
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
