from cache import Cache
from cache import Ram


def test_cache():
    cache = Cache(128, "2-WAY", 4)
    ram = Ram(1, 4)

    # full the cache
    for i in range(cache.no_of_blocks):
        block_data = ram.fetch_data(i)
        cache.write_from_ram(i, block_data)

    for line in cache.cache_lines:
        for block in line:
            if block is None:
                print("####################", end="   ")
                continue
            print(block.get_data(), block.get_tag(), sep=" ", end="   ")
        print()

    block = cache.search(9, 9)

    print(block.get_data(), block.get_tag())
    print(cache.read(block, 2))
    cache.write(block, ["0x00", "0x00", "0x00", "0x00"])

    for line in cache.cache_lines:
        for block in line:
            if block is None:
                print("####################", end="   ")
                continue
            print(block.get_data(), block.get_tag(), sep=" ", end="   ")
        print()


def main():
    test_cache()


if __name__ == "__main__":
    main()
