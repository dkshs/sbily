import contextlib

from django.apps import AppConfig


class LinksConfig(AppConfig):
    name = "sbily.links"

    def ready(self):
        with contextlib.suppress(ImportError):
            import sbily.links.signals  # noqa: F401
