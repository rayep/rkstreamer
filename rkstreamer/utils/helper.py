"""Module with helper functions & classes"""


def parse_input(input_str: str):
    """Return input based on the type"""
    if input_str.isdigit():
        return int(input_str)
    return input_str
