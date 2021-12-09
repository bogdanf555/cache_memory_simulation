from tkinter import Event
from cache import Cache
from cache import Ram
import user_interface


class Controller:
    def __init__(self) -> None:
        self.cache = None
        self.ram = None
        self.user_interface = user_interface.UserInterface()

    def create_cache(self, capacity, associativity, block_size):
        self.cache = Cache(capacity, associativity, block_size)

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
                line_row.append("".join(str(elem) for elem in block.get_data()))
            values.append(line_row)

        return headings, values

    def fill_cache(self):
        if self.cache is None or self.ram is None:
            print("FILL_CACHE: CACHE OR RAM IS NONE")
            return

        for i in range(self.cache.no_of_blocks):
            block_data = self.ram.fetch_data(i)
            self.cache.write_from_ram(i, block_data)

    def event_loop(self):

        while True:
            event, values = self.user_interface.window.read()

            if event == "Exit" or event == user_interface.sg.WIN_CLOSED:
                break

            if event == "Create":

                cache_capacity = int(values["-CACHE_CAPACITY-"])
                associativity = values["-ASSOCIATIVITY-"]
                block_size = int(values["-BLOCK_SIZE-"])

                ram_capacity = int(values["-RAM_CAPACITY-"])

                self.create_cache(cache_capacity, associativity, block_size)
                self.create_ram(ram_capacity, block_size)

                self.fill_cache()

                # create table, add it in window column
                headings, values = self.fetch_cache_data()
                self.user_interface.create_table(headings, values)

                print(self.cache)
                print(self.ram)

            if event == "Start":
                pass


def main():
    Controller().event_loop()


if __name__ == "__main__":
    main()
