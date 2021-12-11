from PyQt5.QtWidgets import QApplication
from cache import Cache
from cache import Ram

import sys

from gui_management import GuiManager


class Controller:
    def __init__(self) -> None:
        self.cache = None
        self.ram = None

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
            headings.append(f"Data {x}")

        for line in self.cache.cache_lines:
            line_row = list()
            for block in line:
                line_row.append(block.get_tag())
                line_row.append("".join(str(elem) + "  " for elem in block.get_data()))
            values.append(line_row)

        return headings, values

    def fill_cache(self):
        if self.cache is None or self.ram is None:
            print("FILL_CACHE: CACHE OR RAM IS NONE")
            return

        for i in range(self.cache.no_of_blocks):
            block_data = self.ram.fetch_data(i)
            self.cache.write_from_ram(i, block_data)


def main():

    app = QApplication(sys.argv)

    controller = Controller()
    gui_manager = GuiManager(controller)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
