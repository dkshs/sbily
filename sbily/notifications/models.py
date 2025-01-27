from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

    TYPE_CHOICES = (
        (SUCCESS, _("Success")),
        (INFO, _("Info")),
        (WARNING, _("Warning")),
        (ERROR, _("Error")),
    )

    title = models.CharField(
        _("Title"),
        max_length=255,
        help_text=_("Notification title"),
    )
    type = models.CharField(
        _("Type"),
        max_length=20,
        choices=TYPE_CHOICES,
        default=INFO,
        help_text=_("Type of notification"),
    )
    content = models.TextField(_("Content"), help_text=_("Notification content"))
    is_read = models.BooleanField(_("Is Read"), default=False, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text=_("User who received this notification"),
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def mark_as_read(self):
        """Mark notification as read and save."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=["is_read"])

    def mark_as_unread(self):
        """Mark notification as unread and save."""
        if self.is_read:
            self.is_read = False
            self.save(update_fields=["is_read"])
