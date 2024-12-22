from django.contrib import messages
from django.http import HttpRequest

from .models import ShortenedLink

MAX_NUM_LINKS_PER_USER = 5
MAX_NUM_LINKS_PER_PREMIUM_USER = 10


def can_user_create_link(request: HttpRequest):
    user = request.user
    links = ShortenedLink.objects.filter(user=user)
    max_num_links = (
        MAX_NUM_LINKS_PER_PREMIUM_USER if user.is_premium else MAX_NUM_LINKS_PER_USER
    )
    if not links.count() < max_num_links:
        if user.is_admin:
            return True
        messages.error(request, f"You can only create {max_num_links} links")
        return False
    return True
