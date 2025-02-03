from django.contrib import admin

from .models import ShortenedLink


@admin.register(ShortenedLink)
class ShortenedLinkAdmin(admin.ModelAdmin):
    list_display = [
        "original_link",
        "shortened_link",
        "created_at",
        "updated_at",
        "remove_at",
        "is_active",
    ]
    list_filter = ["created_at", "updated_at", "is_active"]
    search_fields = ["original_link", "shortened_link", "user__username"]
