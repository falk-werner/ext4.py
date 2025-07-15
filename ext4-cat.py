#!/usr/bin/env python3

import argparse
import sys
import ext4

def do_cat(filename, path):
    with open(filename, 'rb') as f:
        fs = ext4.FileSystem(f)
        id = fs.find(path)
        if id is None:
            print('error: file not found')
            return
        inode = fs.lookup(id)
        if not inode.is_reg():
            print('error: regular file expected')
            return
        remaining = inode.size
        for block in fs.blocks(inode):
            if remaining < len(block):
                block = block[0:remaining]
            sys.stdout.buffer.write(block)
            remaining -= len(block)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str)
    parser.add_argument('path', type=str)
    args = parser.parse_args()
    do_cat(args.filename, args.path)

if __name__ == '__main__':
    main()