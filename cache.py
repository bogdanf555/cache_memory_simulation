import random
import math

import util

class Cache:

    # capacity - size of the cache in bytes
    # block_size - number of bytes in a block (mandatory a power of 2)
    # associativity - directly mapped, fully associative or "K-WAY" (this format, where K is a number > 1)
    def __init__(self, capacity, associativity, block_size):
        
        if not util.is_power_of_two(block_size):
            raise util.CacheError("Block size not a power of two")
        
        if not util.is_power_of_two(capacity):
            raise util.CacheError("Capacity not a power of two")

        self.block_size = block_size
        self.associativity = associativity
        self.tag_size = util.CACHE_ADDRESS_SIZE - math.log2(self.block_size) - math.log2(self.no_of_cache_lines) # in bytes
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
                raise util.CacheError("K-way association too high (NOTE: Block Size * Associativity <= Capacity / 2)")
        else:
            raise util.CacheError("Invalid associativity: " + self.associativity)

        self.cache_lines = [
            [CacheBlock(self.block_size, util.generate_random_tag(self.used_tags, self.tag_size)) for x in range(self.associated)]
                for y in range(self.no_of_cache_lines)]

    # block index in the RAM memory, data to be loaded in the cache block
    def loadBlockFromRAM(self, block_index, data_block):
        
        if self.associativity == util.DIRECTLY_MAPPED:
            self.cache_lines[block_index % self.no_of_cache_lines][0].setData(data_block)
        else:
            if self.associativity == util.FULLY_ASSOCIATIVE:
                line = self.cache_lines[0]
            else:
                line = line = self.cache_lines[block_index % self.no_of_cache_lines]

            placed = False
            for block in line:
                if block.isDataEmpty():
                    block.setData(data_block)
                    placed = True
                    break

            if not placed:
                block = random.choice(line)
                block.setData(data_block)
            
    def search():
        pass


class CacheBlock:

    def __init__(self, block_size, tag):
        self.no_of_cells = block_size
        self.tag = tag
        self.data = [None for i in range(self.no_of_cells)]

    def getDataOctet(self, block_offset):
        return self.data[block_offset]

    def getData(self):
        return self.data
    
    def setData(self, data):
        self.data = data

    def getTag(self):
        return self.tag

    def isDataEmpty(self):
        return not any(self.data)