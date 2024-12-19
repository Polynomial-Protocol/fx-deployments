import math


def round_up(value: float, precision: int):
    return int(math.ceil(value / 10**precision)) * 10**precision
