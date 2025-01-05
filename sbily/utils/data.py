import re

MIN_PASSWORD_LENGTH = 8


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


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validates a password by checking if it meets the following criteria:
    - At least 8 characters long
    - Contains at least one digit
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one special character

    Args:
        password: A string representing the password to be validated.

    Returns:
        tuple[bool, str]: A tuple containing:
            - bool: True if password is valid, False otherwise
            - str: Empty string if valid, error message if invalid
    """
    if not isinstance(password, str):
        return False, "Password must be a string"

    if not password.strip():
        return False, "Password cannot be empty"

    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters"

    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>])"
    if not re.search(pattern, password):
        return False, (
            "Password must contain at least one digit, one uppercase letter, "
            "one lowercase letter, and one special character."
        )

    return True, ""
