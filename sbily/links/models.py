from django.conf import settings
from django.db import models

BASE_URL = getattr(settings, "BASE_URL", None)


class ShortenedLink(models.Model):
    original_link = models.URLField()
    shortened_link = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Shortened Link"
        verbose_name_plural = "Shortened Links"

    def __str__(self):
        return self.shortened_link

    def get_absolute_url(self):
        return f"{BASE_URL}{self.shortened_link}" if BASE_URL else None
