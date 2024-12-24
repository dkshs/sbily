import secrets
from urllib.parse import urljoin

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import IntegrityError
from django.db import models
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from sbily.users.models import User

SITE_BASE_URL = settings.BASE_URL or ""


def future_date_validator(value):
    if value <= timezone.now() + timezone.timedelta(minutes=1):
        raise ValidationError(
            _("The remove_at date must be at least 1 minutes in the future."),
        )


class ShortenedLink(models.Model):
    SHORTENED_LINK_PATTERN = r"^[a-zA-Z0-9-_]*$"
    SHORTENED_LINK_MAX_LENGTH = 10
    MAX_RETRIES = 3

    original_link = models.URLField(
        _("Original URL"),
        max_length=2000,
        help_text=_("The original URL that will be shortened"),
    )
    shortened_link = models.CharField(
        _("Shortened URL"),
        max_length=SHORTENED_LINK_MAX_LENGTH,
        null=True,
        blank=True,
        unique=True,
        db_index=True,
        validators=[
            RegexValidator(
                regex=SHORTENED_LINK_PATTERN,
                message=_(
                    "Shortened link must be alphanumeric with hyphens and underscores only",  # noqa: E501
                ),
            ),
        ],
        error_messages={
            "unique": _("This shortened link already exists"),
            "max_length": _("Shortened link must be at most %s characters long")
            % SHORTENED_LINK_MAX_LENGTH,
        },
        help_text=_("The shortened URL path"),
    )
    created_at = models.DateTimeField(
        _("Created At"),
        auto_now_add=True,
        db_index=True,
        help_text=_("When this shortened link was created"),
    )
    updated_at = models.DateTimeField(
        _("Updated At"),
        auto_now=True,
        help_text=_("When this shortened link was last updated"),
    )
    remove_at = models.DateTimeField(
        _("Remove At"),
        null=True,
        blank=True,
        db_index=True,
        validators=[future_date_validator],
        help_text=_("When this link should be automatically removed"),
    )
    is_active = models.BooleanField(
        _("Is Active"),
        default=True,
        db_index=True,
        help_text=_("Whether this shortened link is active"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shortened_links",
        help_text=_("User who created this shortened link"),
    )

    class Meta:
        verbose_name = _("Shortened Link")
        verbose_name_plural = _("Shortened Links")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["shortened_link", "user"]),
        ]

    def __str__(self) -> str:
        status = _("Temporary") if self.remove_at else _("Permanent")
        return f"{self.shortened_link} ({status})"

    @transaction.atomic
    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        if not self.shortened_link:
            self._generate_unique_shortened_link()
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Returns the absolute URL for this shortened link"""
        path = reverse("redirect_link", kwargs={"shortened_link": self.shortened_link})
        return urljoin(SITE_BASE_URL, path)

    def clean(self):
        user = self.user
        if not user.can_create_link() and not user.can_create_temporary_link():
            raise ValidationError(
                _(
                    "You have reached the maximum number of links allowed for your account. "  # noqa: E501
                    "Please upgrade your account to create more links.",
                ),
                code="max_links_reached",
            )
        return super().clean()

    def _generate_unique_shortened_link(self) -> None:
        """Helper method to generate unique shortened link with retries"""
        for retry in range(self.MAX_RETRIES):
            try:
                self.shortened_link = secrets.token_urlsafe(6)[
                    : self.SHORTENED_LINK_MAX_LENGTH
                ]
                self.full_clean()
                break
            except (IntegrityError, ValidationError) as e:
                if (
                    isinstance(e, IntegrityError)
                    and "unique constraint" not in str(e.args).lower()
                ):
                    raise
                if retry == self.MAX_RETRIES - 1:
                    raise ValidationError(
                        _("Could not generate unique shortened link"),
                    ) from e

    def is_expired(self) -> bool:
        """Check if the link has expired based on remove_at timestamp"""
        now = timezone.now()
        return bool(self.remove_at and self.remove_at <= now)

    def is_functional(self) -> bool:
        """Check if the link is functional based on is_active and remove_at timestamp"""
        return self.is_active and not self.is_expired()

    def time_until_expiration(self) -> timezone.timedelta | None:
        """Returns the time remaining until link expiration or None if permanent"""
        if not self.remove_at or self.is_expired():
            return None
        now = timezone.now()
        return self.remove_at - now
