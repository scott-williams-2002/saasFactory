from random import choices
from string import ascii_letters, digits

def generate_random_id(length: int = 8) -> str:
    """
    Generate a unique ID of a specified length.
    Args:
        length (int): The length of the ID (default is 8).
    Returns:
        str: The unique ID.
    """
    return ''.join(choices(ascii_letters + digits, k=length))