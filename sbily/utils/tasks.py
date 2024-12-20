from typing import Any


def get_task_response(
    status: str,
    message: str = "",
    error: str | None = None,
    **kwargs,
) -> dict[str, Any]:
    """Helper function to standardize task responses

    Args:
        status: Status of the task (e.g. 'success', 'error', 'pending')
        message: Description or details about the task result
        error: Error message if task failed
        **kwargs: Additional data to include in response

    Returns:
        Dict containing standardized response with status, message and data
    """
    response = {
        "status": status,
        "message": message,
        "data": kwargs or None,
    }
    if error:
        response["error"] = error
    return response
