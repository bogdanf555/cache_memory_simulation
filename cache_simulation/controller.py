from re import search
from PyQt5.QtWidgets import QApplication
from cache import Cache
from cache import Ram
import util

import sys
import random

from gui_management import GuiManager


class Controller:
    def __init__(self) -> None:
        self.cache = None
        self.ram = None
        self.cache_records = []

    def create_cache(
        self, capacity, associativity, block_size, replacement_strategy, write_policy
    ):
        self.cache = Cache(
            capacity, associativity, block_size, replacement_strategy, write_policy
        )

    def create_ram(self, capacity, block_size):
        self.ram = Ram(capacity, block_size)

    def fetch_cache_data(self):

        if self.cache is None or self.ram is None:
            print("FETCH_CACHE_DATA: CACHE OR RAM IS NONE")
            return

        values = []
        headings = []

        for x in range(self.cache.associated):
            headings.append(f"Tag {x}")

            if self.cache.strategy == util.ReplacementStrategy.FIRST_IN_FIRST_OUT:
                headings.append("FP")
            elif self.cache.strategy == util.ReplacementStrategy.LEAST_FREQUENTLY_USED:
                headings.append("AC")
            elif self.cache.strategy in (
                util.ReplacementStrategy.LEAST_RECENTLY_USED,
                util.ReplacementStrategy.MOST_RECENTLY_USED,
            ):
                headings.append("AT")

            if self.cache.write_policy == util.WritePolicy.WRITE_ONCE:
                headings.append("WO")
                headings.append("DB")
            elif self.cache.write_policy == util.WritePolicy.WRITE_BACK:
                headings.append("DB")

            headings.append(f"Data {x}")

        for line in self.cache.cache_lines:
            line_row = list()
            for block in line:
                line_row.append(block.get_tag())

                if self.cache.strategy == util.ReplacementStrategy.FIRST_IN_FIRST_OUT:
                    line_row.append(block.get_fifo_place())
                elif (
                    self.cache.strategy
                    == util.ReplacementStrategy.LEAST_FREQUENTLY_USED
                ):
                    line_row.append(block.get_accessed_count())
                elif self.cache.strategy in (
                    util.ReplacementStrategy.LEAST_RECENTLY_USED,
                    util.ReplacementStrategy.MOST_RECENTLY_USED,
                ):
                    line_row.append(block.get_access_time())

                if self.cache.write_policy == util.WritePolicy.WRITE_ONCE:
                    line_row.append(block.get_written())
                    line_row.append(block.get_dirty_bit())
                elif self.cache.write_policy == util.WritePolicy.WRITE_BACK:
                    line_row.append(block.get_dirty_bit())

                line_row.append("".join(str(elem) + "  " for elem in block.get_data()))
            values.append(line_row)

        return (headings, values)

    def fill_cache(self):
        if self.cache is None or self.ram is None:
            print("FILL_CACHE: CACHE OR RAM IS NONE")
            return

        for i in range(self.cache.no_of_blocks):
            block_data = self.ram.fetch_data(i)
            self.cache.write_from_ram(i, block_data)

        self.cache_records.append(self.fetch_cache_data())

    def random_read_or_write(self, index, tag, with_miss=False):
        operation = random.randint(0, 1)  # 0 means read, 1 means write

        block = self.cache.search(tag, index)
        operation_name = "_with_hit" if not with_miss else "_with_miss"

        if operation:
            operation_name = "write" + operation_name
            data = [hex(random.randint(0, 255)) for x in range(self.cache.block_size)]
            self.cache.write(block, data)

        else:
            operation_name = "read" + operation_name
            data = self.cache.read(block)

        result = " ".join(elem for elem in data)

        self.cache_records.append(self.fetch_cache_data())

        return (operation_name, tag, index, result)

    def read_and_write_all_blocks_once(self):

        operations = []

        for index, line in enumerate(self.cache.cache_lines):
            for block in line:
                tag = block.get_tag()

                # search
                block_found = self.cache.search(tag, index)
                # read
                data = self.cache.read(block_found)
                result = " ".join(elem for elem in data)
                operations.append(("read_with_hit", tag, index, result))

                self.cache_records.append(self.fetch_cache_data())

                # write
                new_data = [hex(random.randint(0, 255)) for x in data]
                self.cache.write(block_found, new_data)
                result = " ".join(elem for elem in new_data)
                operations.append(("write_with_hit", tag, index, result))

                self.cache_records.append(self.fetch_cache_data())

        return operations

    def read_and_write_blocks_randomly(self):

        operations = []
        no_operations = int(self.cache.no_of_blocks / 2)

        for i in range(no_operations):
            random_tag = random.randint(0, self.cache.no_of_blocks - 1)

            if self.cache.associativity == util.FULLY_ASSOCIATIVE:
                index = 0
            else:
                index = random_tag % self.cache.no_of_cache_lines

            operation = self.random_read_or_write(index, random_tag)
            operations.append(operation)

        return operations

    def replace_blocks(self):

        operations = []

        if self.cache.associativity == util.DIRECTLY_MAPPED:
            no_operations = int(self.cache.no_of_blocks / 4)

            for i in range(no_operations):
                tag = random.randint(self.cache.no_of_blocks, self.ram.index_count - 1)

                replacement_block = self.ram.fetch_data(tag)
                self.cache.write_from_ram(tag, replacement_block)

                operation = self.random_read_or_write(
                    (tag % self.cache.no_of_cache_lines), tag, True
                )
                operations.append(operation)

        elif self.cache.associativity == util.FULLY_ASSOCIATIVE:
            no_operations = int(self.cache.no_of_blocks / 4)

            for i in range(no_operations):
                tag = random.randint(self.cache.no_of_blocks, self.ram.index_count - 1)

                replacement_block = self.ram.fetch_data(tag)
                self.cache.write_from_ram(tag, replacement_block)

                operation = self.random_read_or_write(0, tag, True)
                operations.append(operation)
        else:
            for index in range(self.cache.no_of_cache_lines):
                tag = random.randint(self.cache.no_of_blocks, self.ram.index_count - 1)

                modulo = tag % self.cache.no_of_cache_lines
                if modulo < index:
                    tag += index - modulo
                elif modulo > index:
                    tag += (
                        self.cache.no_of_cache_lines
                        - tag % self.cache.no_of_cache_lines
                        + index
                    )

                replacement_block = self.ram.fetch_data(tag)
                self.cache.write_from_ram(tag, replacement_block)

                operation = self.random_read_or_write(index, tag, True)
                operations.append(operation)

        return operations


def main():

    app = QApplication(sys.argv)

    controller = Controller()
    gui_manager = GuiManager(controller)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
