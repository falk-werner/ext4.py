#!/usr/bin/env python3

from dataclasses import dataclass

SUPERBLOCK_OFFSET = 1024
SUPERBLOCK_SIZE = 1024

SB_OFFSET_TOTAL_INDOES = 0
SB_OFFSET_TOTAL_BLOCKS_LO = 4
SB_OFFSET_TOTAL_BLOCKS_HI = 0x150
SB_OFFSET_RESERVED_BLOCKS_LO = 8
SB_OFFSET_FREE_BLOCKS_LO = 12
SB_OFFSET_FREE_INODES = 16
SB_OFFSET_FIRST_DATA_BLOCK = 20
SB_OFFSET_BLOCK_SIZE = 24
SB_OFFSET_BLOCKS_PER_GROUP = 32
SB_OFFSET_INODES_PER_GROUP = 40
SB_OFFSET_EXT2_SIGNATURE = 56
SB_OFFSET_STATE = 58
SB_OFFSET_ERRORS = 60
SB_OFFSET_MINOR_REVISION = 62
SB_OFFSET_CREATOR_OS = 72
SB_OFFSET_REVISION = 76
SB_OFFSET_FIRST_INODE = 84
SB_OFFSET_INODE_SIZE = 88
SB_OFFSET_REQUIRED_FEATURES = 96
SB_OFFSET_CHECKSUM = 1020
SB_OFFSET_BG_DESCR_SIZE = 0xFE
SB_OFFSET_FEATURE_COMPAT = 0x5C
SB_OFFSET_FEATURE_INCOMPAT = 0x60
SB_OFFSET_FEATURE_RO_COMPAT = 0x64
SB_OFFSET_UUID = 0x068
SB_OFFSET_VOLUME_NAME = 0x78

SB_UUID_SIZE = 16
SB_VOLUME_NAME_SIZE= 16
SB_EXT2_SIGNATURE = 0xef53
SB_FEATURE_64BIT = 0x80

BG_OFFSET_BLOCK_BITMAP = 0
BG_OFFSET_INODE_BITMAP = 4
BG_OFFSET_INODE_TABLE  = 8

INO_OFFSET_MODE = 0
INO_OFFSET_UID = 2
INO_OFFSET_SIZE_LO = 4
INO_OFFSET_GID = 24
INO_OFFSET_FLAGS = 0x20
INO_OFFSET_BLOCK = 40
INO_BLOCK_SIZE = 60

INO_FLAG_EXTENDS     = 0x00080000
INO_FLAG_INLINE_DATA = 0x10000000

INO_DIRECT_BLOCKPOINTERS_SIZE = 12
INO_OFFSET_DIRECT_BLOCKPOINTERS = 0
INO_OFFSET_SINGLY_INDIRECT_BLOCKPOINTERS = 48
INO_OFFSET_DOUBLY_INDIRECT_BLOCKPOINTERS= 52
INO_OFFSET_TRIPLY__INDIRECT_BLOCKPOINTERS = 56

MODE_OTHER_EXECUTE    = 0x0001
MODE_OTHER_WRITE      = 0x0002
MODE_OTHER_READ       = 0x0004
MODE_GROUP_EXECUTE    = 0x0008
MODE_GROUP_WRITE      = 0x0010
MODE_GROUP_READ       = 0x0020
MODE_USER_EXECUTE     = 0x0040
MODE_USER_WRITE       = 0x0080
MODE_USER_READ        = 0x0100
MODE_STICKY           = 0x0200
MODE_SUID             = 0x0400
MODE_SGID             = 0x0800
MODE_TYPE_MASK        = 0xf000
MODE_FIFO             = 0x1000
MODE_CHARACTER_DEVICE = 0x2000
MODE_DIRECTORY        = 0x4000
MODE_BLOCK_DEVICE     = 0x6000
MODE_REGULAR_FILE     = 0x8000
MODE_SYMBOLIC_LINK    = 0xA000
MODE_UNIX_SOCKET      = 0xC000

def is_dir(mode):
    return (mode & MODE_TYPE_MASK) == MODE_DIRECTORY

class Reader:
    def __init__(self, data):
        self.data = data

    def u32(self, offset):
        value = 0
        for i in range(0,4):
            value <<= 8
            value += self.data[offset + 3 - i]
        return value
    
    def u16(self, offset):
        high = self.data[offset + 1]
        low  = self.data[offset + 0]
        value = (high << 8) + low
        return value
    
    def bytes(self, offset, count):
        return self.data[offset: offset + count]


class Superblock:
    def __init__(self, file):
        file.seek(SUPERBLOCK_OFFSET)
        data = file.read(SUPERBLOCK_SIZE)
        reader = Reader(data)

        signature = reader.u16(SB_OFFSET_EXT2_SIGNATURE)
        if signature != SB_EXT2_SIGNATURE:
            raise Exception('invalid signature')

        self.total_blocks = reader.u32(SB_OFFSET_TOTAL_BLOCKS_LO)
        self.total_inodes = reader.u32(SB_OFFSET_TOTAL_INDOES)
        self.reserved_blocks = reader.u32(SB_OFFSET_RESERVED_BLOCKS_LO)
        self.free_blocks = reader.u32(SB_OFFSET_FREE_BLOCKS_LO)
        self.free_inodes = reader.u32(SB_OFFSET_FREE_INODES)
        self.first_data_block = reader.u32(SB_OFFSET_FIRST_DATA_BLOCK)
        self.blocks_per_group = reader.u32(SB_OFFSET_BLOCKS_PER_GROUP)
        self.inodes_per_group = reader.u32(SB_OFFSET_INODES_PER_GROUP)
        self.state = reader.u16(SB_OFFSET_STATE)
        self.errors = reader.u16(SB_OFFSET_ERRORS)
        self.minor_revision = reader.u16(SB_OFFSET_MINOR_REVISION)
        self.creator_os = reader.u32(SB_OFFSET_CREATOR_OS)
        self.revision = reader.u32(SB_OFFSET_REVISION)
        self.first_ino = 11
        self.inode_size = 128
        self.uuid = b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0'
        self.volume_name = ''
        self.bg_descriptor_size = 32

        ld_block_size = reader.u32(SB_OFFSET_BLOCK_SIZE)
        if ld_block_size > 6:
            raise Exception('block size above 64KByte is not supported')
        self.block_size = 1 << (10 + ld_block_size)

        if self.revision >= 1:
            total_blocks_high = reader.u32(SB_OFFSET_TOTAL_BLOCKS_HI)
            self.total_blocks += total_blocks_high << 32

            self.inode_size = reader.u16(SB_OFFSET_INODE_SIZE)
            self.feature_compat = reader.u32(SB_OFFSET_FEATURE_COMPAT)
            self.feature_incompat = reader.u32(SB_OFFSET_FEATURE_INCOMPAT)
            self.feature_ro_compat = reader.u32(SB_OFFSET_FEATURE_RO_COMPAT)
            self.uuid = reader.bytes(SB_OFFSET_UUID, SB_UUID_SIZE)
            self.volume_name = reader.bytes(SB_OFFSET_VOLUME_NAME, SB_VOLUME_NAME_SIZE).decode('utf-8')

            if (self.feature_incompat & SB_FEATURE_64BIT) != 0:
                self.bg_descriptor_size = reader.u16(SB_OFFSET_BG_DESCR_SIZE)

        self.gd_offset = (self.first_data_block + 1) * self.block_size

class BlockGroup:
    def __init__(self, file, offset, size):
        file.seek(offset)
        data = file.read(size)
        reader = Reader(data)

        self.block_bitmap = reader.u32(BG_OFFSET_BLOCK_BITMAP)
        self.inode_bitmap = reader.u32(BG_OFFSET_INODE_BITMAP)
        self.inode_table  = reader.u32(BG_OFFSET_INODE_TABLE)

class INode:
    def __init__(self, file, offset, size):
        file.seek(offset)
        data = file.read(size)
        reader = Reader(data)

        self.mode = reader.u16(INO_OFFSET_MODE)
        self.uid  = reader.u16(INO_OFFSET_UID)
        self.gid  = reader.u16(INO_OFFSET_GID)
        self.size = reader.u32(INO_OFFSET_SIZE_LO)
        self.flags = reader.u32(INO_OFFSET_FLAGS)
        self.block = reader.bytes(INO_OFFSET_BLOCK, INO_BLOCK_SIZE)

@dataclass
class DirEntry:
    inode_id : int
    type: int
    name : str

class FileSystem:
    def __init__(self, file):
        self.file = file
        self.superblock = Superblock(file)
    
    def lookup(self, inode_id):
        if (inode_id == 0) or (inode_id > self.superblock.total_inodes):
            raise Exception('invalid inode id')
    
        blockgroup_id = int( (inode_id - 1) / self.superblock.inodes_per_group )
        blockgroup = self.get_blockgroup(blockgroup_id)

        inode_table_offset = blockgroup.inode_table * self.superblock.block_size
        inode_index = (inode_id - 1) % self.superblock.inodes_per_group
        inode_offset = inode_table_offset + (inode_index * self.superblock.inode_size)

        inode = INode(self.file, inode_offset, self.superblock.inode_size)
        return inode


    def get_blockgroup(self, blockgroup_id) -> BlockGroup:
        count = int( (self.superblock.total_blocks + self.superblock.blocks_per_group - 1) / self.superblock.blocks_per_group )
        if blockgroup_id > count:
            raise Exception('invalid blockgroup id')
        
        offset = self.superblock.gd_offset + ( blockgroup_id * self.superblock.bg_descriptor_size)

        blockgroup = BlockGroup(self.file, offset, self.superblock.bg_descriptor_size)
        return blockgroup
    
    def get_block(self, block_id):
        offset = block_id * self.superblock.block_size
        self.file.seek(offset)
        return self.file.read(self.superblock.block_size)

    def blocks(self, inode: INode):
        if (inode.flags & INO_FLAG_INLINE_DATA) != 0:
            yield inode.block
        elif (inode.flags & INO_FLAG_EXTENDS) != 0:
            pass
        else:
            reader = Reader(inode.block)
            for i in range(0, INO_DIRECT_BLOCKPOINTERS_SIZE):
                block_id = reader.u32(INO_OFFSET_DIRECT_BLOCKPOINTERS + (i * 4))
                if block_id != 0:
                    block = self.get_block(block_id)
                    yield block
            # ToDo: iterate singly indirect block pointers
            # ToDo: iterate doubly indirect block pointers
            # ToDo: iterate triply indirect block pointers

    def files(self, inode_id):
        inode = self.lookup(inode_id)

        if not is_dir(inode.mode):
            raise Exception("Directory expected")
        
        for block in self.blocks(inode):
            reader = Reader(block)
            offset = 0

            while offset < len(block):
                inode_id = reader.u32(offset)
                record_size = reader.u16(offset + 4)

                if inode_id != 0:                    
                    name_length = block[offset + 6]                    
                    type = block[offset + 7]
                    name = reader.bytes(offset + 8, name_length).decode('utf-8')
                    entry = DirEntry(inode_id, type, name)
                    yield entry
                
                offset += record_size

    def find(self, path):
        if path.startswith('/'):
            path = path[1:]
        id = 2
        for elem in path.split('/'):
            found = False
            for file in self.files(id):
                if file.name == elem:
                    id = file.inode_id
                    found = True
                    break
            if not found:
                return None
        return id
