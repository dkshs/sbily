from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _

from .models import Token
from .models import User


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "email", "email_verified")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "max_num_links",
                    "max_num_links_temporary",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "role",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ["user", "type", "created_at", "expires_at"]
    list_filter = ["type", "created_at", "expires_at"]
    search_fields = ["user__username", "type", "token"]
    ordering = ["-created_at"]
    index_together = ["user", "type", "created_at"]
