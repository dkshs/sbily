import hashlib
import secrets


def generate_token(length: int = 32):
    """
    Generates a secure token of 64 characters.

    Args:
        length (int): The desired length of the random bytes used to generate the token.
            This value is used as input to the SHA256 hash function. The final token
            will always be 64 characters long. Defaults to 32.

    Returns:
        str: A secure token of 64 characters.
    """
    return hashlib.sha256(secrets.token_bytes(length)).hexdigest()
