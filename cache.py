import random
import math

import util
from util import CacheError, ReplacementStrategy, WritePolicy


class Cache:

    # capacity - size of the cache in bytes
    # block_size - number of bytes in a block (mandatory a power of 2)
    # associativity - directly mapped, fully associative or "K-WAY" (this format, where K is a number > 1)
    def __init__(self, capacity, associativity, block_size):

        if not util.is_power_of_two(block_size):
            raise util.CacheError("Block size not a power of two")

        if not util.is_power_of_two(capacity):
            raise util.CacheError("Capacity not a power of two")

        self.strategy = ReplacementStrategy.RANDOM
        self.write_policy = WritePolicy.WRITE_THROUGH
        self.block_size = block_size
        self.associativity = associativity
        self.tag_size = (
            util.CACHE_ADDRESS_SIZE
            - math.log2(self.block_size)
            - math.log2(self.no_of_cache_lines)
        )  # in bytes
        self.used_tags = []

        if self.associativity == util.DIRECTLY_MAPPED:
            self.no_of_cache_lines = capacity / self.block_size
            self.associated = 1
        elif self.associativity == util.FULLY_ASSOCIATIVE:
            self.no_of_cache_lines = 1
            self.associated = capacity / self.block_size
        elif util.is_k_way(self.associativity):
            self.associated = util.extrack_k_from_k_way(associativity)
            self.no_of_cache_lines = capacity / (self.associated * self.block_size)
            if self.no_of_cache_lines < 2:
                raise util.CacheError(
                    "K-way association too high (NOTE: Block Size * Associativity <= Capacity / 2)"
                )
        else:
            raise util.CacheError("Invalid associativity: " + self.associativity)

        self.cache_lines = [
            [
                CacheBlock(
                    self.block_size,
                    util.generate_random_tag(self.used_tags, self.tag_size),
                    -1,
                )
                for x in range(self.associated)
            ]
            for y in range(self.no_of_cache_lines)
        ]

    def block_replacement(self, line, data_block):
        # TODO : implement the actual logic of cache block replacement by strategy

        # NOTE : you also have to simulate the saving of block if dirty bit is set

        if self.strategy == ReplacementStrategy.RANDOM:
            block = random.choice(line)
            block.setData(data_block)
        elif self.strategy == ReplacementStrategy.LEAST_FREQUENTLY_USED:
            pass
        elif self.strategy == ReplacementStrategy.LEAST_RECENTLY_USED:
            pass
        elif self.strategy == ReplacementStrategy.MOST_RECENTLY_USED:
            pass
        elif self.strategy == ReplacementStrategy.FIRST_IN_FIRST_OUT:
            pass
        else:
            raise CacheError("invalid replacement strategy")

    # block index in the RAM memory, data to be loaded in the cache block
    def loadBlockFromRAM(self, block_index, data_block):

        if self.associativity == util.DIRECTLY_MAPPED:
            block = self.cache_lines[block_index % self.no_of_cache_lines][0]
            block.setData(data_block)
            block.set_ram_index(block_index)
        else:
            if self.associativity == util.FULLY_ASSOCIATIVE:
                line = self.cache_lines[0]
            else:
                line = self.cache_lines[block_index % self.no_of_cache_lines]

            placed = False
            for block in line:
                if block.isDataEmpty():
                    block.setData(data_block)
                    placed = True
                    break

            if not placed:
                self.block_replacement()

    # NOTE : shall return block if found, None otherwise
    def search(self):
        pass

    # NOTE : you also have to simulate the saving of block if dirty bit is set
    def write(self, block, data):

        if self.write_policy == WritePolicy.WRITE_THROUGH:
            pass
        elif self.write_policy == WritePolicy.WRITE_BACK:
            pass
        elif self.write_policy == WritePolicy.WRITE_ONCE:
            pass
        else:
            raise CacheError("invalid write policy")

        block.set_accessed_count(block.get_accessed_count + 1)
        block.set_written(True)
        block.set_dirty_bit(
            True
        )  # TODO : see when actually you have to set the dirty bit cause it seems wrong here (consider the writting policy)

    def read(self, block, block_offset=None):  # access byte in block or entire block
        if block_offset:
            return block.get_data_byte(block_offset)
        return block.get_data()

    def write_back_to_ram(self):
        pass


class CacheBlock:
    def __init__(self, block_size, tag, ram_index):
        self.no_of_cells = block_size
        self.tag = tag
        self.data = [None for i in range(self.no_of_cells)]
        self.ram_index = ram_index
        self.dirty_bit = False  # NOTE : for write back policy
        self.accessed_count = 0
        self.written = False  # NOTE : for write once policy

    def get_data_byte(self, block_offset):
        return self.data[block_offset]

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def set_ram_index(self, index):
        self.ram_index = index

    def get_tag(self):
        return self.tag

    def is_data_empty(self):
        return not any(self.data)

    def set_accessed_count(self, count):
        self.accessed_count = count

    def get_accessed_count(self):
        return self.accessed_count

    def set_written(self, value):
        self.written = value

    def get_written(self):
        return self.written

    def set_dirty_bit(self, value):
        self.dirty_bit = value

    def get_dirty_bit(self):
        return self.dirty_bit


class RAM:
    def __init__(self, size_in_megabytes, block_size_in_bytes):
        self.size_in_megabytes = size_in_megabytes
        self.block_size_in_bytes = block_size_in_bytes
        self.index_count = size_in_megabytes * 1024 * 1024 / self.block_size_in_bytes

    def fetch_data(self, block_index):
        return [
            (util.RRIME_ONE * block_index + util.PRIME_TWO * index) % util.BYTE_MAX
            for index in range(self.block_size_in_bytes)
        ]
