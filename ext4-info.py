#!/usr/bin/env python3


import argparse
import ext4

def print_info(filename):
    with open(filename, 'rb') as f:
        fs = ext4.FileSystem(f)
        sb = fs.superblock

        print('[ superblock.basic ]')
        print(f'total blocks: {sb.total_blocks}')
        print(f'total inodes: {sb.total_inodes}')
        print(f'reserved blocks: {sb.reserved_blocks}')
        print(f'free blocks: {sb.free_blocks}')
        print(f'free inodes: {sb.free_inodes}')
        print(f'first data block: {sb.first_data_block}')
        print(f'blocks per group: {sb.blocks_per_group}')
        print(f'inodes per group: {sb.inodes_per_group}')
        print(f'state: {sb.state}')
        print(f'errors: {sb.errors}')
        print(f'revision: {sb.revision}.{sb.minor_revision}')
        print(f'creator os: {sb.creator_os}')

        print('[ superblock.extended ]')
        print(f'first inode: {sb.first_ino}')
        print(f'inode size: {sb.inode_size}')
        print(f'compatible features: {sb.feature_compat}')
        print(f'incompatible features: {sb.feature_incompat}')
        print(f'ready-only compatible features: {sb.feature_ro_compat}')
        print(f'blockgrounp descriptor size: {sb.bg_descriptor_size}')
        print(f'uuid: {sb.uuid}')
        print(f'volume name: {sb.volume_name}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str)
    args = parser.parse_args()
    print_info(args.filename)

if __name__ == '__main__':
    main()
