from urllib.parse import urljoin

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.timezone import datetime
from django.utils.timezone import now
from django.utils.timezone import timedelta
from django.utils.translation import gettext_lazy as _

from .utils.data import generate_token

BASE_URL = settings.BASE_URL or ""


class User(AbstractUser):
    DEACTIVATED_USER_RETENTION = 7  # days

    ROLE_ADMIN = "admin"
    ROLE_USER = "user"
    ROLE_PREMIUM = "premium"

    MAX_NUM_LINKS_PER_USER = 5
    MAX_NUM_LINKS_PER_PREMIUM_USER = 10
    MAX_NUM_LINKS_TEMP_PER_USER = 2
    MAX_NUM_LINKS_TEMP_PER_PREMIUM_USER = 5

    ROLE_CHOICES = [
        (ROLE_ADMIN, _("Admin")),
        (ROLE_USER, _("User")),
        (ROLE_PREMIUM, _("Premium")),
    ]

    role = models.CharField(
        _("role"),
        max_length=10,
        choices=ROLE_CHOICES,
        default=ROLE_USER,
        help_text=_("User role"),
    )
    email = models.EmailField(_("email address"), unique=True, blank=False, null=False)
    email_verified = models.BooleanField(
        _("email verified"),
        default=False,
        help_text=_("Designates whether the user has verified their email address."),
    )
    login_with_email = models.BooleanField(
        _("login with email"),
        default=False,
        help_text=_("Designates whether the user can login with email."),
    )
    max_num_links = models.PositiveIntegerField(
        _("max number of links"),
        default=MAX_NUM_LINKS_PER_USER,
        help_text=_("Maximum number of links a user can create"),
    )
    max_num_links_temporary = models.PositiveIntegerField(
        _("max number of temporary links"),
        default=MAX_NUM_LINKS_TEMP_PER_USER,
        help_text=_("Maximum number of temporary links a user can create"),
    )

    @property
    def is_admin(self) -> bool:
        return self.role == self.ROLE_ADMIN

    @property
    def is_user(self) -> bool:
        return self.role == self.ROLE_USER

    @property
    def is_premium(self) -> bool:
        return self.role == self.ROLE_PREMIUM

    @property
    def link_num(self) -> dict[str, int]:
        """Returns the number of links and temporary links created by user"""
        shortened_links = self.shortened_links.all()
        links = shortened_links.filter(remove_at__isnull=True).count()
        temp_links = shortened_links.filter(remove_at__isnull=False).count()
        return {"links": links, "temp_links": temp_links}

    @property
    def link_num_left(self) -> dict[str, int]:
        """Returns the number of links and temporary links left for user"""
        link_num = self.link_num
        return {
            "links": max(0, self.max_num_links - link_num["links"]),
            "temp_links": max(0, self.max_num_links_temporary - link_num["temp_links"]),
        }

    def save(self, *args, **kwargs):
        role_limits = {
            self.ROLE_ADMIN: (100, 100),
            self.ROLE_PREMIUM: (
                self.MAX_NUM_LINKS_PER_PREMIUM_USER,
                self.MAX_NUM_LINKS_TEMP_PER_PREMIUM_USER,
            ),
            self.ROLE_USER: (
                self.MAX_NUM_LINKS_PER_USER,
                self.MAX_NUM_LINKS_TEMP_PER_USER,
            ),
        }

        if self.is_superuser:
            self.role = self.ROLE_ADMIN
            self.email_verified = True

        if self.role in role_limits:
            self.max_num_links, self.max_num_links_temporary = role_limits[self.role]

        super().save(*args, **kwargs)

    def can_create_link(self) -> bool:
        """Check if user can create links"""
        return self.link_num_left["links"] > 0

    def can_create_temporary_link(self) -> bool:
        """Check if user can create temporary links"""
        return self.link_num_left["temp_links"] > 0

    def get_full_name(self) -> str:
        """Return user's full name or username if not set"""
        return super().get_full_name() or self.username

    def get_short_name(self) -> str:
        """Return user's short name or username if not set"""
        return super().get_short_name() or self.username

    def get_token(
        self,
        token_type: str,
        expires_at: None | datetime = None,
    ) -> str:
        """Gets a token of the given type.

        Args:
            token_type: Type of token to get/create
            expires_at: Optional expiry time for the token

        Returns:
            str: The token string

        Raises:
            ValueError: If token_type is not valid
        """
        if token_type not in dict(Token.TOKEN_TYPE):
            msg = f"Invalid token type: {token_type}"
            raise ValueError(msg)

        token = self.tokens.filter(type=token_type).first() or self.tokens.create(
            type=token_type,
            expires_at=expires_at,
        )

        if token.is_expired():
            token.renew()

        return token.token

    def get_token_link(
        self,
        token_type: str,
        url_name: str,
        expires_at: None | datetime = None,
    ) -> str:
        """Gets a link for a token of the given type.

        Args:
            token_type: Type of token to get/create
            url_name: Name of URL pattern to generate link
            expires_at: Optional expiry time for the token

        Returns:
            str: Full URL containing the token
        """
        token = self.get_token(token_type, expires_at)
        path = reverse(url_name, kwargs={"token": token})
        return urljoin(BASE_URL, path)

    def get_verify_email_link(self) -> str:
        """Generate email verification link for user"""
        if self.email_verified:
            raise ValidationError(_("User email is already verified"), code="verified")

        return self.get_token_link(Token.TYPE_EMAIL_VERIFICATION, "verify_email")

    def get_reset_password_link(self) -> str:
        """Generate password reset link for user"""
        return self.get_token_link(Token.TYPE_PASSWORD_RESET, "reset_password")

    def get_account_activation_link(self) -> str:
        """Generate account activation link for user"""
        deactivated_user_retention = timedelta(
            days=self.DEACTIVATED_USER_RETENTION,
        )
        return self.get_token_link(
            Token.TYPE_ACTIVATE_ACCOUNT,
            "activate_account_verify",
            expires_at=now() + deactivated_user_retention,
        )

    def email_user(
        self,
        subject: str,
        template: str,
        **kwargs,
    ):
        """Send an email to a user with given subject and template.

        Args:
            subject: Email subject
            template: Path to the email template
            **kwargs: Additional context data for the email template
        """
        from .utils.emails import send_email_to_user

        send_email_to_user(
            self,
            subject,
            template,
            **kwargs,
        )


class Token(models.Model):
    DEFAULT_EXPIRY = timedelta(hours=2)
    TYPE_EMAIL_VERIFICATION = "email_verification"
    TYPE_SIGN_IN_WITH_EMAIL = "sign_in_with_email"
    TYPE_PASSWORD_RESET = "password_reset"  # noqa: S105
    TYPE_ACTIVATE_ACCOUNT = "activate_account"

    TOKEN_TYPE = [
        (TYPE_EMAIL_VERIFICATION, _("Email Verification")),
        (TYPE_SIGN_IN_WITH_EMAIL, _("Sign In With Email")),
        (TYPE_PASSWORD_RESET, _("Password Reset")),
        (TYPE_ACTIVATE_ACCOUNT, _("Activate Account")),
    ]

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
        default=TYPE_EMAIL_VERIFICATION,
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
            self.expires_at = now() + self.DEFAULT_EXPIRY
        if not self.token:
            self.token = generate_token()
        super().full_clean()
        super().save(*args, **kwargs)

    def renew(self):
        """Renew token by updating token and timestamps"""
        self.token = generate_token()
        self.expires_at = now() + self.DEFAULT_EXPIRY
        self.save()
        return self.token

    def is_expired(self):
        """Check if token is expired"""
        return self.expires_at and now() > self.expires_at

    def clean(self):
        """Validate token instance"""
        if self.is_expired():
            raise ValidationError(_("This token has expired."), code="expired")
        if not self.user.is_active and self.type != self.TYPE_ACTIVATE_ACCOUNT:
            raise ValidationError(
                _("This user is not active."),
                code="inactive",
            )
        if self.type == self.TYPE_ACTIVATE_ACCOUNT and self.user.is_active:
            raise ValidationError(
                _("This account has already been activated."),
                code="activated",
            )
        if self.type == self.TYPE_EMAIL_VERIFICATION and self.user.email_verified:
            raise ValidationError(
                _("This email has already been verified."),
                code="verified",
            )
        if self.type == self.TYPE_SIGN_IN_WITH_EMAIL and not self.user.email_verified:
            raise ValidationError(
                _("This email has not been verified."),
                code="unverified",
            )
        super().clean()
