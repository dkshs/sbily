class BadRequestError(Exception):
    """Custom exception class for handling bad request errors.

    Args:
        message (str): The error message to be displayed
        redirect_url (str | None): Optional URL to redirect to after error (default: None)
    """  # noqa: E501

    def __init__(self, message: str, redirect_url: str | None = None) -> None:
        self.redirect_url = redirect_url
        self.message = message
        super().__init__(self.message)


def bad_request_error(message: str, redirect_url: str | None = None) -> None:
    """Helper function to raise BadRequestError with a message.

    Args:
        message (str): The error message to be displayed
        redirect_url (str | None): Optional URL to redirect to after error (default: None)

    Raises:
        BadRequestError: Always raises this exception with the provided message
    """  # noqa: E501
    raise BadRequestError(message=message, redirect_url=redirect_url)
