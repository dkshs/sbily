import hashlib
import secrets


def generate_token(length: int = 32):
    """
    Generates a secure token of the specified length.

    Args:
        length (int): The desired length of the token. Defaults to 32.

    Returns:
        str: A secure token of the specified length.
    """
    return hashlib.sha256(secrets.token_bytes(length)).hexdigest()
