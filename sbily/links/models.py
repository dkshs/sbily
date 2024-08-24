from django.conf import settings
from django.db import models
from django.urls import reverse

from sbily.users.models import User

BASE_URL: str | None = getattr(settings, "BASE_URL", None)


class ShortenedLink(models.Model):
    original_link = models.URLField()
    shortened_link = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    remove_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Shortened Link"
        verbose_name_plural = "Shortened Links"

    def __str__(self):
        is_temporary = " - Temporary" if self.remove_at else ""
        return f"{self.shortened_link}{is_temporary}"

    def get_absolute_url(self):
        path = reverse("redirect_link", kwargs={"shortened_link": self.shortened_link})
        return f"{BASE_URL}{path.lstrip('/')}"
