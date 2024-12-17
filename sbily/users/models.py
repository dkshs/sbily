from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("user", "User"),
        ("premium", "Premium"),
    ]
    role = models.CharField(
        _("role"),
        max_length=10,
        choices=ROLE_CHOICES,
        default="user",
        help_text=_("User role"),
    )

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_user(self):
        return self.role == "user"

    @property
    def is_premium(self):
        return self.role == "premium"

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = "admin"
        super().save(*args, **kwargs)

    def get_full_name(self):
        return super().get_full_name() or self.username
