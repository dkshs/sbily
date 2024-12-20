import hashlib
import secrets


def validate(fields: list[str]) -> bool:
    """
    Validates a list of fields by checking if
    each field is not empty after stripping whitespace.

    Args:
        fields: A list of strings representing fields to be validated.

    Returns:
        bool: True if all fields are not empty after stripping whitespace,
        False otherwise.
    """
    return all(str(field).strip() != "" for field in fields)


def generate_token(length: int = 32):
    """
    Generates a secure token of the specified length.

    Args:
        length (int): The desired length of the token. Defaults to 32.

    Returns:
        str: A secure token of the specified length.
    """
    return hashlib.sha256(secrets.token_bytes(length)).hexdigest()
