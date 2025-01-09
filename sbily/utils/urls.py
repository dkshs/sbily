from urllib.parse import urlencode

from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from sbily.utils.data import is_none


def redirect_with_params(
    url_name: str,
    params: dict | None = None,
) -> HttpResponseRedirect:
    """Redirects to a URL with optional query parameters.

    Args:
        url_name: The name of the URL pattern.
        params: A dictionary of query parameters.

    Returns:
        An HTTP redirect response.

    Example:
        >>> redirect_with_params("sign_in", {"next": "/account/me/"})
        HttpResponseRedirect("/auth/sign_in/?next=/account/me/")
    """
    if not params:
        return redirect(url_name)

    filtered_params = {k: v for k, v in params.items() if not is_none(v)}
    if not filtered_params:
        return redirect(url_name)

    query_string = urlencode(filtered_params)
    url_path = reverse(url_name)

    return redirect(f"{url_path}?{query_string}")
