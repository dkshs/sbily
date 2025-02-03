import contextlib

from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "sbily.users"

    def ready(self):
        with contextlib.suppress(ImportError):
            import sbily.users.signals  # noqa: F401
