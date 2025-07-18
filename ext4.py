#!/usr/bin/env python3

"""Readonly access to ext4 files."""

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

ROOT = 2

DIRENT_UNKNOWN = 0
DIRENT_REG     = 1
DIRENT_DIR     = 2
DIRENT_CHAR    = 3
DIRENT_BLOCK   = 4
DIRENT_FIFO    = 5
DIRENT_SOCKET  = 6
DIRENT_SYMLINK = 7

class Reader:
    """Read access to byte buffer."""

    def __init__(self, data):
        self.data = data

    def u32(self, offset):
        """Read u32 value at a given offset."""
        value = 0
        for i in range(0,4):
            value <<= 8
            value += self.data[offset + 3 - i]
        return value

    def u16(self, offset):
        """Read u16 value at a given offset."""
        high = self.data[offset + 1]
        low  = self.data[offset + 0]
        value = (high << 8) + low
        return value

    def bytes(self, offset, count):
        """Read a number of bytes at a given offset."""
        return self.data[offset: offset + count]

@dataclass
# pylint: disable=too-many-instance-attributes
class Superblock:
    """Ext2/3/4 superblock."""
    def __init__(self, data):
        reader = Reader(data)

        signature = reader.u16(SB_OFFSET_EXT2_SIGNATURE)
        if signature != SB_EXT2_SIGNATURE:
            raise RuntimeError('invalid signature')

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
            raise RuntimeError('block size above 64KByte is not supported')
        self.block_size = 1 << (10 + ld_block_size)

        if self.revision >= 1:
            total_blocks_high = reader.u32(SB_OFFSET_TOTAL_BLOCKS_HI)
            self.total_blocks += total_blocks_high << 32

            self.inode_size = reader.u16(SB_OFFSET_INODE_SIZE)
            self.feature_compat = reader.u32(SB_OFFSET_FEATURE_COMPAT)
            self.feature_incompat = reader.u32(SB_OFFSET_FEATURE_INCOMPAT)
            self.feature_ro_compat = reader.u32(SB_OFFSET_FEATURE_RO_COMPAT)
            self.uuid = reader.bytes(SB_OFFSET_UUID, SB_UUID_SIZE)
            self.volume_name = reader.bytes(SB_OFFSET_VOLUME_NAME,
                SB_VOLUME_NAME_SIZE).decode('utf-8')

            if (self.feature_incompat & SB_FEATURE_64BIT) != 0:
                self.bg_descriptor_size = reader.u16(SB_OFFSET_BG_DESCR_SIZE)

        self.gd_offset = (self.first_data_block + 1) * self.block_size

@dataclass
class BlockGroup:
    """Ext2/3/4 block group."""
    def __init__(self, data):
        reader = Reader(data)

        self.block_bitmap = reader.u32(BG_OFFSET_BLOCK_BITMAP)
        self.inode_bitmap = reader.u32(BG_OFFSET_INODE_BITMAP)
        self.inode_table  = reader.u32(BG_OFFSET_INODE_TABLE)

class INode:
    """Index node."""
    def __init__(self, data):
        reader = Reader(data)

        self.mode = reader.u16(INO_OFFSET_MODE)
        self.uid  = reader.u16(INO_OFFSET_UID)
        self.gid  = reader.u16(INO_OFFSET_GID)
        self.size = reader.u32(INO_OFFSET_SIZE_LO)
        self.flags = reader.u32(INO_OFFSET_FLAGS)
        self.block = reader.bytes(INO_OFFSET_BLOCK, INO_BLOCK_SIZE)

    def is_dir(self):
        """Returns True, if inode is a directory."""
        return (self.mode & MODE_TYPE_MASK) == MODE_DIRECTORY

    def is_reg(self):
        """Returns True, if inode is a regular file."""
        return (self.mode & MODE_TYPE_MASK) == MODE_REGULAR_FILE

    def is_symlink(self):
        return (self.mode & MODE_TYPE_MASK) == MODE_SYMBOLIC_LINK

    def is_socket(self):
        return (self.mode & MODE_TYPE_MASK) == MODE_UNIX_SOCKET

    def is_fifo(self):
        return (self.mode & MODE_TYPE_MASK) == MODE_FIFO

    def is_char(self):
        return (self.mode & MODE_TYPE_MASK) == MODE_CHARACTER_DEVICE

    def is_block(self):
        return (self.mode & MODE_TYPE_MASK) == MODE_BLOCK_DEVICE


@dataclass
class DirEntry:
    """Directory entry."""
    inode_id : int
    type: int
    name : str

class BlockIterator:
    def __init__(self, core):
        self.__core = core

    def __indirect_blocks(self, blockpointers_id):
        if blockpointers_id != 0:
            blockpointers = self.__core.block(blockpointers_id)
            reader = Reader(blockpointers)
            for i in range(0, int( len(blockpointers) / 4)):
                block_id = reader.u32(i * 4)
                block = self.__core.block(block_id)
                yield block

    def __doubly_indirect_blocks(self, blockpointers_id):
        if blockpointers_id != 0:
            blockpointers = self.__core.block(blockpointers_id)
            reader = Reader(blockpointers)
            for i in range(0, int( len(blockpointers) / 4)):
                block_id = reader.u32(i * 4)
                for block in self.__indirect_blocks(block_id):
                    yield block

    def __triply_indirect_blocks(self, blockpointers_id):
        if blockpointers_id != 0:
            blockpointers = self.__core.block(blockpointers_id)
            reader = Reader(blockpointers)
            for i in range(0, int( len(blockpointers) / 4)):
                block_id = reader.u32(i * 4)
                for block in self.__doubly_indirect_blocks(block_id):
                    yield block

    def blocks(self, inode):
            reader = Reader(inode.block)
            for i in range(0, INO_DIRECT_BLOCKPOINTERS_SIZE):
                block_id = reader.u32(INO_OFFSET_DIRECT_BLOCKPOINTERS + (i * 4))
                if block_id != 0:
                    block = self.__core.block(block_id)
                    yield block

            # iterate singly indirect block pointers
            block_id = reader.u32(INO_OFFSET_SINGLY_INDIRECT_BLOCKPOINTERS)
            for block in self.__indirect_blocks(block_id):
                yield block

            # iterate doubly indirect block pointers
            block_id = reader.u32(INO_OFFSET_SINGLY_INDIRECT_BLOCKPOINTERS)
            for block in self.__doubly_indirect_blocks(block_id):
                yield block

            # iterate triply indirect block pointers
            block_id = reader.u32(INO_OFFSET_SINGLY_INDIRECT_BLOCKPOINTERS)
            for block in self.__triply_indirect_blocks(block_id):
                yield block

class Core:
    def __init__(self, file):
        self.__file = file
        self.superblock = Superblock(self.__read(SUPERBLOCK_OFFSET, SUPERBLOCK_SIZE))

    def __read(self, offset, size):
        self.__file.seek(offset)
        return self.__file.read(size)

    def lookup(self, inode_id):
        """Returns the inode of the given inode id."""
        if (inode_id == 0) or (inode_id > self.superblock.total_inodes):
            raise ValueError('invalid inode id')

        blockgroup_id = int( (inode_id - 1) / self.superblock.inodes_per_group )
        blockgroup = self.__blockgroup(blockgroup_id)

        inode_table_offset = blockgroup.inode_table * self.superblock.block_size
        inode_index = (inode_id - 1) % self.superblock.inodes_per_group
        inode_offset = inode_table_offset + (inode_index * self.superblock.inode_size)

        data = self.__read(inode_offset, self.superblock.inode_size)
        inode = INode(data)
        return inode


    def __blockgroup(self, blockgroup_id) -> BlockGroup:
        count = int( (self.superblock.total_blocks +
            self.superblock.blocks_per_group - 1) / self.superblock.blocks_per_group )
        if blockgroup_id > count:
            raise ValueError('invalid blockgroup id')

        offset = self.superblock.gd_offset + ( blockgroup_id * self.superblock.bg_descriptor_size)
        data = self.__read(offset, self.superblock.bg_descriptor_size)
        blockgroup = BlockGroup(data)
        return blockgroup

    def block(self, block_id):
        offset = block_id * self.superblock.block_size
        return self.__read(offset, self.superblock.block_size)

class FileSystem:
    """Ext2/3/4 filesystem."""
    def __init__(self, file):
        self.__core = Core(file)

    def info(self):
        return self.__core.superblock

    def lookup(self, inode_id):
        return self.__core.lookup(inode_id)

    def blocks(self, inode: INode):
        """Iterator over all blocks of an inode."""
        if (inode.flags & INO_FLAG_INLINE_DATA) != 0:
            yield inode.block
        elif (inode.flags & INO_FLAG_EXTENDS) != 0:
            raise NotImplementedError('extends not supported yet')
        else:
            it = BlockIterator(self.__core)
            for block in it.blocks(inode):
                yield block

    def files(self, inode_id):
        """Iterator over all entries of the directory specified by the given inode."""
        inode = self.__core.lookup(inode_id)

        if not inode.is_dir():
            raise ValueError("Directory expected")

        for block in self.blocks(inode):
            reader = Reader(block)
            offset = 0

            while offset < len(block):
                inode_id = reader.u32(offset)
                record_size = reader.u16(offset + 4)

                if inode_id != 0:
                    name_length = block[offset + 6]
                    filetype = block[offset + 7]
                    name = reader.bytes(offset + 8, name_length).decode('utf-8')
                    entry = DirEntry(inode_id, filetype, name)
                    yield entry

                offset += record_size

    def find(self, path):
        """Returns the inode id of the given path."""
        if path.startswith('/'):
            path = path[1:]
        inode_id = 2
        for elem in path.split('/'):
            if elem == '':
                continue
            found = False
            for file in self.files(inode_id):
                if file.name == elem:
                    inode_id = file.inode_id
                    found = True
                    break
            if not found:
                return None
        return inode_id
