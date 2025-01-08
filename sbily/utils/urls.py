from urllib.parse import urlencode

from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from sbily.utils.data import is_none


def redirect_with_params(
    url_name: str,
    params: dict | None = None,
) -> HttpResponseRedirect:
    """
    Simulates a redirect to a given URL with parameters.

    This function takes a URL and a dictionary of parameters, and returns a redirect response
    with the parameters appended as a query string.

    Args:
        url_name (str): Name of the URL pattern to redirect to
        params (dict | None): A dictionary of parameter key-value pairs to be appended to the URL.

    Returns:
        HttpResponseRedirect: A redirect response with parameters.

    Example:
        >>> redirect_with_params("sign_in", {"next": "/account/me/"})
        HttpResponseRedirect("/auth/sign_in/?next=/account/me/")
    """  # noqa: E501
    if params is None:
        return redirect(url_name)

    filtered_params = {k: v for k, v in params.items() if not is_none(v)}
    if not filtered_params:
        return redirect(url_name)

    query_string = urlencode(filtered_params)
    url_path = reverse(url_name)

    return redirect(f"{url_path}?{query_string}")
