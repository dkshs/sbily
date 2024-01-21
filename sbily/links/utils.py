from django.contrib import messages
from django.core.validators import URLValidator

from .models import ShortenedLink
import re


def link_is_valid(request, original_link: str, shortened_link: str):
    REGEX = r"^[a-zA-Z0-9_-]+$"
    if not original_link.strip():
        messages.error(request, "Please enter an original link")
        return False
    if not shortened_link.strip():
        messages.error(request, "Please enter a shortened link")
        return False
    if ShortenedLink.objects.filter(shortened_link=shortened_link).exists():
        messages.error(request, "Shortened link already exists")
        return False
    if not re.match(REGEX, shortened_link):
        messages.error(request, "Shortened link must only contain letters, numbers, underscores, and dashes")
        return False
    if len(shortened_link.strip()) > 10:
        messages.error(request, "Shortened link must be 10 characters or less")
        return False
    validator = URLValidator()
    try:
        validator(original_link)
    except Exception:
        messages.error(request, "Invalid original link")
        return False
    return True
