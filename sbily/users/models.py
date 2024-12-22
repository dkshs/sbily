from datetime import UTC
from datetime import datetime
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .utils.data import generate_token

BASE_URL = settings.BASE_URL.removesuffix("/")


class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", _("Admin")),
        ("user", _("User")),
        ("premium", _("Premium")),
    ]
    role = models.CharField(
        _("role"),
        max_length=10,
        choices=ROLE_CHOICES,
        default="user",
        help_text=_("User role"),
    )
    email_verified = models.BooleanField(
        _("email verified"),
        default=False,
        help_text=_("Designates whether the user has verified their email address."),
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
            self.email_verified = True
        super().save(*args, **kwargs)

    def get_full_name(self):
        return super().get_full_name() or self.username

    def get_short_name(self):
        return super().get_short_name() or self.username

    def get_verify_email_link(self):
        if not self.email:
            raise ValidationError(_("User has no email address"), code="no_email")
        if self.email_verified:
            raise ValidationError(_("User email is already verified"), code="verified")

        token = self.tokens.filter(
            type="email_verification",
        ).first() or self.tokens.create(type="email_verification")
        if token.is_expired():
            token.renew()

        return BASE_URL + reverse(
            "verify_email",
            kwargs={"token": token.token},
        )


class Token(models.Model):
    TOKEN_TYPE = [
        ("email_verification", _("Email Verification")),
        ("password_reset", _("Password Reset")),
    ]
    DEFAULT_EXPIRY = timedelta(hours=2)

    token = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        editable=False,
        help_text=_("Unique token string"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tokens",
        help_text=_("User this token belongs to"),
    )
    type = models.CharField(
        max_length=20,
        choices=TOKEN_TYPE,
        default="email_verification",
        help_text=_("Type of token"),
    )
    expires_at = models.DateTimeField(
        db_index=True,
        editable=False,
        help_text=_("Token expiration date and time"),
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "type", "created_at"])]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "type"],
                name="unique_user_token_type",
            ),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.type} - {self.token}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = datetime.now(UTC) + self.DEFAULT_EXPIRY
        if not self.token:
            self.token = generate_token()
        super().save(*args, **kwargs)

    def renew(self):
        """Renew token by updating token and timestamps

        Returns:
            str: New token
        """
        self.token = generate_token()
        now = datetime.now(UTC)
        self.created_at = now
        self.expires_at = now + self.DEFAULT_EXPIRY
        self.save()
        return self.token

    def is_expired(self):
        """Check if token is expired

        Returns:
            bool: True if token is expired, False otherwise
        """
        return datetime.now(UTC) > self.expires_at

    def clean(self):
        super().clean()
        if self.is_expired():
            raise ValidationError(_("This token has expired."), code="expired")
        if self.type == "email_verification" and self.user.email_verified:
            raise ValidationError(
                _("This email has already been verified."),
                code="verified",
            )
        if self.type == "password_reset" and not self.user.email_verified:
            raise ValidationError(
                _("This email has not been verified."),
                code="unverified",
            )
