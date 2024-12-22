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
