from django.conf import settings
from django.urls import include
from django.urls import path

from . import views

LINK_PREFIX = getattr(settings, "LINK_PREFIX", "")

# URLs for managing individual links
link_urlpatterns = [
    path("", views.link, name="link"),
    path("update/", views.update_link, name="update_link"),
    path("delete/", views.delete_link, name="delete_link"),
]

# URLs for managing deleted links
deleted_links_urlpatterns = [
    path("", views.deleted_links, name="deleted_links"),
    path("<str:shortened_link>/restore/", views.restore_link, name="restore_link"),
    path(
        "<str:shortened_link>/remove/",
        views.remove_deleted_link,
        name="remove_deleted_link",
    ),
]

# Main URL patterns
urlpatterns = [
    # Core pages
    path("", views.home, name="home"),
    path("create_link/", views.create_link, name="create_link"),
    # Link redirection
    path(
        "{prefix}<str:shortened_link>/".format(prefix=LINK_PREFIX or ""),
        views.redirect_link,
        name="redirect_link",
    ),
    # Include sub-patterns
    path("link/<str:shortened_link>/", include(link_urlpatterns)),
    path("deleted_links/", include(deleted_links_urlpatterns)),
    path("handle_link_actions/", views.handle_link_actions, name="handle_link_actions"),
]
