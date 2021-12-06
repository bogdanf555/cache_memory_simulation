import random

import util
from util import CacheError, ReplacementStrategy, WritePolicy
from queue import Queue


class Cache:

    # capacity - size of the cache in bytes
    # block_size - number of bytes in a block (mandatory a power of 2)
    # associativity - directly mapped, fully associative or "K-WAY" (this format, where K is a number > 1)
    def __init__(self, capacity, associativity, block_size):

        if not util.is_power_of_two(block_size):
            raise util.CacheError("Block size not a power of two")

        if not util.is_power_of_two(capacity):
            raise util.CacheError("Capacity not a power of two")

        self.no_of_blocks = int(capacity / block_size)
        self.strategy = ReplacementStrategy.RANDOM
        self.write_policy = WritePolicy.WRITE_THROUGH
        self.block_size = block_size
        self.associativity = associativity

        self.global_access_time = 0

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

        self.no_of_cache_lines = int(self.no_of_cache_lines)

        self.cache_lines = [
            [None for x in range(self.associated)]
            for y in range(self.no_of_cache_lines)
        ]

    def block_replacement(self, line, block):

        # NOTE : you also have to simulate the saving of block if dirty bit is set
        replaced_block = None

        if self.strategy == ReplacementStrategy.RANDOM:
            index = random.randint(len(line))
        elif self.strategy == ReplacementStrategy.LEAST_FREQUENTLY_USED:
            index = line.index(min(line, key=lambda x: x.get_accessed_count()))
        elif self.strategy == ReplacementStrategy.LEAST_RECENTLY_USED:
            index = line.index(min(line, key=lambda x: x.get_access_time()))
        elif self.strategy == ReplacementStrategy.MOST_RECENTLY_USED:
            index = line.index(max(line, key=lambda x: x.get_access_time()))
        elif self.strategy == ReplacementStrategy.FIRST_IN_FIRST_OUT:
            index = line.index(min(line, key=lambda x: x.get_fifo_place()))
            [block.decrement_fifo_place() for block in line]
        else:
            raise CacheError("invalid replacement strategy")

        replaced_block = line[index]
        line[index] = block
        # save the replaced block
        if self.write_policy in [WritePolicy.WRITE_BACK, WritePolicy.WRITE_ONCE]:
            self.write_back_to_ram(replaced_block.get_tag(), replaced_block.get_data())

    # block index in the RAM memory, data to be loaded in the cache block
    def write_from_ram(self, block_index, data_block):

        if self.associativity == util.DIRECTLY_MAPPED:
            line_index = block_index % self.no_of_cache_lines
            replaced_block = self.cache_lines[line_index][0]
            self.cache_lines[line_index][0] = CacheBlock(
                self.block_size, block_index, -1, data_block
            )

            if replaced_block:
                if self.write_policy in [
                    WritePolicy.WRITE_BACK,
                    WritePolicy.WRITE_ONCE,
                ]:
                    self.write_back_to_ram(
                        replaced_block.get_tag(), replaced_block.get_data()
                    )

        else:
            line = None
            if self.associativity == util.FULLY_ASSOCIATIVE:
                line = self.cache_lines[0]
            else:
                line = self.cache_lines[block_index % self.no_of_cache_lines]

            fifo_place = sum(x is not None for x in line)
            new_block = CacheBlock(self.block_size, block_index, fifo_place, data_block)

            placed = False
            for index, block in enumerate(line):
                if block is None:
                    line[index] = new_block
                    placed = True
                    break

            if not placed:
                self.block_replacement(line, new_block)

    # NOTE : shall return block if found, None otherwise
    def search(self, tag, index=0):

        line = self.cache_lines[index]
        for x in line:
            if x is not None and x.get_tag() == tag:
                return x

        return None

    # NOTE : you also have to simulate the saving of block if dirty bit is set
    def write(self, block, data):

        self.global_access_time += 1
        block.set_access_time(self.global_access_time)

        if self.write_policy == WritePolicy.WRITE_THROUGH:
            block.set_data(data)
            self.write_back_to_ram(block.get_tag(), data)
        elif self.write_policy == WritePolicy.WRITE_BACK:
            block.set_data(data)
            block.set_dirty_bit(True)
        elif self.write_policy == WritePolicy.WRITE_ONCE:
            block.set_data(data)
            if not block.get_written:
                self.write_back_to_ram(block.get_tag(), data)
            else:
                block.set_dirty_bit(True)
        else:
            raise CacheError("invalid write policy")

        block.increment_access_count()
        block.set_written(True)

    def read(self, block, block_offset=None):  # access byte in block or entire block

        self.global_access_time += 1
        block.set_access_time(self.global_access_time)

        block.increment_access_count()
        if block_offset:
            return block.get_data_byte(block_offset)
        return block.get_data()

    def write_back_to_ram(self, block_index, data):
        pass  # Should not do anything actually :))

    def get_write_policy(self):
        return self.write_policy

    def set_write_policy(self, policy: WritePolicy):
        self.write_policy = policy

    def get_strategy(self):
        return self.strategy

    def set_strategy(self, strategy: ReplacementStrategy):
        self.strategy = strategy


class CacheBlock:
    def __init__(self, block_size, tag, fifo_place, data=None):
        self.no_of_cells = block_size
        self.tag = tag
        if data:
            self.data = data
        else:
            self.data = [None for i in range(self.no_of_cells)]
        self.dirty_bit = False  # NOTE : for write back policy
        self.accessed_count = 0  # MOST/LAST frequently used replacement policy
        self.written = False  # NOTE : for write once policy
        self.fifo_place = fifo_place
        self.access_time = -1

    def get_data_byte(self, block_offset):
        return self.data[block_offset]

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def get_access_time(self):
        return self.access_time

    def set_access_time(self, time):
        self.access_time = time

    def get_tag(self):
        return self.tag

    def get_fifo_place(self):
        return self.fifo_place

    def is_data_empty(self):
        return not any(self.data)

    def increment_access_count(self):
        self.accessed_count += 1

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


class Ram:
    def __init__(self, size_in_megabytes, block_size_in_bytes):
        self.size_in_megabytes = size_in_megabytes
        self.block_size_in_bytes = block_size_in_bytes
        self.index_count = size_in_megabytes * 1024 * 1024 / self.block_size_in_bytes

    def fetch_data(self, block_index):
        return [
            hex((util.PRIME_ONE * block_index + util.PRIME_TWO * index) % util.BYTE_MAX)
            for index in range(self.block_size_in_bytes)
        ]
