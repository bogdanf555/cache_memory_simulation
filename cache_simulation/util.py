import re
import random
import string
from enum import Enum

CELL_SIZE = 8
FULLY_ASSOCIATIVE = "fully_associative"
DIRECTLY_MAPPED = "directly_mapped"
CACHE_ADDRESS_SIZE = 32

PRIME_ONE = 997
PRIME_TWO = 1009
BYTE_MAX = 256

# (n & (n-1) == 0) and n != 0 -- check if the number is power of two using bitwise manipulation
def is_power_of_two(number):

    if type(number) != int:
        raise ValueError("The provided variable is not an integer")

    if number < 0:
        return False

    return (number & (number - 1) == 0) and number != 0


def generate_random_tag(list_of_used_tags, tag_size):

    generated_tag = "".join(
        random.choice(string.ascii_letters) for i in range(tag_size)
    )
    while generated_tag in list_of_used_tags:
        generated_tag = "".join(
            random.choice(string.ascii_letters) for i in range(tag_size)
        )

    list_of_used_tags.append(generated_tag)
    return generated_tag


# verifies if a strings is of form "K-WAY" where K is a number > 2
def is_k_way(associativity):
    match_object = re.search("^([2-9][0-9]*)-WAY$", associativity)
    return match_object != None and int(match_object.group(1)) > 1


def extrack_k_from_k_way(associativity):
    if is_k_way(associativity):
        return int(re.search("^([2-9][0-9]*)-WAY$", associativity).group(1))

    raise CacheError(associativity + "is not in K-WAY format")


class CacheError(Exception):
    pass


class ReplacementStrategy(Enum):
    RANDOM = 1
    LEAST_RECENTLY_USED = 2
    FIRST_IN_FIRST_OUT = 3
    LEAST_FREQUENTLY_USED = 4
    MOST_RECENTLY_USED = 5


class WritePolicy(Enum):
    WRITE_THROUGH = 1
    WRITE_BACK = 2
    WRITE_ONCE = 3
