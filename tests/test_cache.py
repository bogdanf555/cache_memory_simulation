def test_cache():
    cache = ch.Cache(128, "4-WAY", 4)
    ram = ch.Ram(1, 4)

    # full the cache
    for i in range(cache.no_of_blocks):
        block_data = ram.fetch_data(i)
        cache.write_from_ram(i, block_data)

    print(cache)

    block = cache.search(15, 7)

    print(block.get_data(), block.get_tag())
    print(cache.read(block, 2))
    print()

    cache.write(block, ["0x00", "0x00", "0x00", "0x00"])

    print(cache)


test_cache()
