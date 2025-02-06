import re
from typing import Any

from django.contrib.auth.password_validation import (
    validate_password as django_validate_password,
)
from django.core.exceptions import ValidationError

MIN_PASSWORD_LENGTH = 8
SPECIAL_CHARS = r"[!@#$%^&*(),.?\":{}|<>]"
PASSWORD_PATTERN = rf"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*{SPECIAL_CHARS})"


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
    if not isinstance(fields, list):
        return False
    return all(str(field).strip() != "" for field in fields)


def is_none(value: Any) -> bool:
    """Checks if a value is None or a string representing a None-like value."""
    if isinstance(value, str):
        return value.strip().lower() in ("", "none", "null", "undefined")
    return value is None


def validate_password(password: str, user=None) -> tuple[bool, str]:
    """
    Validates a password by checking if it meets the following criteria:
    - At least 8 characters long
    - Contains at least one digit
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one special character (!@#$%^&*(),.?":{}|<>)

    Args:
        password: A string representing the password to be validated.

    Returns:
        tuple[bool, str]: A tuple containing:
            - bool: True if password is valid, False otherwise
            - str: Empty string if valid, error message if invalid

    Examples:
        >>> validate_password("Ab1!defgh")
        (True, "")
        >>> validate_password("abc")
        (False, "Password must be at least 8 characters.")
    """
    if not isinstance(password, str):
        return False, "Password must be a string."

    if not password.strip():
        return False, "Password cannot be empty."

    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters."

    if not re.search(PASSWORD_PATTERN, password):
        return False, (
            "Password must contain at least one digit, one uppercase letter, "
            "one lowercase letter, and one special character."
        )

    try:
        django_validate_password(password, user)
    except ValidationError as e:
        return False, str(e)

    return True, ""
