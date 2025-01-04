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
from django.utils.timesince import timesince
from django.utils.translation import gettext_lazy as _

from sbily.users.models import User

from .managers import DeletedShortenedLinkManager
from .utils import filter_dict
from .utils import user_can_create_link

SITE_BASE_URL = settings.BASE_URL or ""


def future_date_validator(value: timezone.datetime) -> None:
    one_minute_from_now = timezone.now() + timezone.timedelta(minutes=1)
    time_difference = timezone.localtime(value) - one_minute_from_now
    if time_difference.total_seconds() < 0:
        raise ValidationError(
            _("You must put %(value)s in the future.")
            % {"value": timesince(value, one_minute_from_now)},
        )


class AbstractShortenedLink(models.Model):
    SHORTENED_LINK_PATTERN = r"^[a-zA-Z0-9-_]*$"
    SHORTENED_LINK_MAX_LENGTH = 10
    DEFAULT_EXPIRY = timezone.timedelta(days=1)
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
                    "Shortened link must be alphanumeric with "
                    "hyphens and underscores only",
                ),
            ),
        ],
        error_messages={
            "unique": _("This shortened link already exists"),
            "max_length": _(
                "Shortened link must be at most {0} characters long",
            ).format(SHORTENED_LINK_MAX_LENGTH),
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
        abstract = True
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

    def _generate_unique_shortened_link(self) -> None:
        """Helper method to generate unique shortened link with retries"""
        for retry in range(self.MAX_RETRIES):
            try:
                self.shortened_link = secrets.token_urlsafe(8)[
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
                        _(
                            "Could not generate unique shortened link "
                            "after {0} attempts",
                        ).format(self.MAX_RETRIES),
                    ) from e

    def is_expired(self) -> bool:
        """Check if the link has expired based on remove_at timestamp"""
        return bool(self.remove_at and self.remove_at <= timezone.now())

    def is_functional(self) -> bool:
        """Check if the link is functional based on is_active and remove_at timestamp"""
        return self.is_active and not self.is_expired()

    def time_until_expiration(self) -> timezone.timedelta | None:
        """Returns the time remaining until link expiration or None if permanent"""
        if not self.remove_at or self.is_expired():
            return None
        return self.remove_at - timezone.now()


class ShortenedLink(AbstractShortenedLink):
    def clean(self) -> None:
        user_can_create_link(self.id, self.remove_at, self.user)
        super().clean()


class DeletedShortenedLink(AbstractShortenedLink):
    PREMIUM_DELETE_DAYS = 6
    REGULAR_DELETE_DAYS = 3

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="deleted_shortened_links",
        help_text=_("User who created this shortened link"),
    )
    removed_at = models.DateTimeField(
        _("Removed At"),
        auto_now_add=True,
        db_index=True,
        help_text=_("When this shortened link was removed"),
    )

    objects = DeletedShortenedLinkManager()

    class Meta:
        verbose_name = _("Deleted Shortened Link")
        verbose_name_plural = _("Deleted Shortened Links")
        ordering = ["-removed_at"]

    @property
    def time_until_permanent_deletion(self) -> timezone.timedelta:
        """Returns the time remaining until permanent deletion"""
        user = self.user
        delete_links_days = (
            self.PREMIUM_DELETE_DAYS
            if user.is_premium or user.is_admin
            else self.REGULAR_DELETE_DAYS
        )
        return self.removed_at + timezone.timedelta(days=delete_links_days)

    @property
    def time_until_permanent_deletion_formatted(self) -> str:
        """
        Returns the time remaining until permanent deletion in a human-readable format.
        """
        return timesince(timezone.now(), self.time_until_permanent_deletion)

    @transaction.atomic
    def restore(self) -> None:
        """Restore the deleted shortened link"""
        data = filter_dict(self.__dict__.copy(), {"_state", "id", "removed_at"})
        if self.is_expired():
            data["remove_at"] = timezone.now() + self.DEFAULT_EXPIRY
        ShortenedLink.objects.create(**data)
        self.delete()
