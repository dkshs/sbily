# ruff: noqa: BLE001
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.http import HttpRequest
from django.shortcuts import redirect
from django.shortcuts import render

from sbily.links.models import ShortenedLink
from sbily.users.models import Token
from sbily.users.models import User
from sbily.users.tasks import send_password_changed_email
from sbily.users.tasks import send_password_reset_email
from sbily.users.tasks import send_welcome_email
from sbily.utils.data import is_none
from sbily.utils.data import validate
from sbily.utils.data import validate_password
from sbily.utils.errors import BadRequestError
from sbily.utils.errors import bad_request_error
from sbily.utils.urls import redirect_with_params
from sbily.utils.urls import reverse_with_params

from .tasks import send_sign_in_with_email


def sign_up(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method != "POST":
        return render(request, "sign_up.html")

    first_name = request.POST.get("first_name", "")
    last_name = request.POST.get("last_name", "")
    username = request.POST.get("username", "")
    email = request.POST.get("email", "")
    password = request.POST.get("password", "")

    try:
        if not validate([username, email]):
            bad_request_error("Please fill in all fields")
        password_id_valid = validate_password(password)
        if not password_id_valid[0]:
            bad_request_error(password_id_valid[1])
        if User.objects.filter(username=username).exists():
            bad_request_error("User already exists")

        user = User.objects.create_user(
            username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        messages.success(
            request,
            "User created successfully! Please verify your email",
        )
        login(request, user)
        send_welcome_email.delay_on_commit(user.id)
        return redirect("home")
    except BadRequestError as e:
        messages.error(request, e.message)
        return redirect("sign_up")
    except Exception as e:
        messages.error(request, f"Error creating user: {e}")
        return redirect("sign_up")


def sign_in(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("my_account")

    if request.method != "POST":
        next_param = request.GET.get("next", "my_account")
        original_link = request.GET.get("original_link", None)
        context = {"next": next_param, "original_link": original_link}
        return render(request, "sign_in.html", context)

    username = request.POST.get("username", "")
    password = request.POST.get("password", "")

    next_param = request.POST.get("next", "my_account")
    original_link = request.POST.get("original_link", None)
    context = {"next": next_param, "original_link": original_link}

    try:
        if not validate([username, password]):
            bad_request_error("Please fill in all fields")

        user = authenticate(request, username=username, password=password)
        if user is None:
            bad_request_error("Invalid username or password")

        login(request, user)
        if is_none(original_link):
            return redirect("my_account" if is_none(next_param) else next_param)
        url_validate = URLValidator()
        try:
            url_validate(original_link)
            link = ShortenedLink.objects.create(original_link=original_link, user=user)
            messages.success(request, "Link created successfully")
            return redirect("link", shortened_link=link.shortened_link)
        except ValidationError:
            bad_request_error("Invalid original link.")
    except BadRequestError as e:
        messages.error(request, e.message)
        return redirect_with_params("sign_in", context)
    except Exception as e:
        messages.error(request, f"Error signing in: {e}")
        return redirect_with_params("sign_in", context)


def sign_in_with_email(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("my_account")
    if request.method != "POST":
        return render(request, "sign_in_with_email.html")

    email = request.POST.get("email", "")

    try:
        if not validate([email]):
            bad_request_error("Please fill in all fields")

        user = User.objects.get(email=email)
        if not user.email_verified:
            bad_request_error("Please verify your email first")
        if not user.login_with_email:
            bad_request_error("Please enable login with email")

        send_sign_in_with_email.delay_on_commit(user.id)
        messages.success(request, "Please check your email for a sign in link")
        return redirect("sign_in")
    except User.DoesNotExist:
        messages.error(request, "User does not exist")
        return redirect("sign_in_with_email")
    except BadRequestError as e:
        messages.error(request, e.message)
        return redirect("sign_in_with_email")
    except Exception as e:
        messages.error(request, f"Error sending sign in link: {e}")
        return redirect("sign_in_with_email")


def sign_in_with_email_verify(request: HttpRequest, token: str):
    if request.user.is_authenticated:
        return redirect("my_account")

    try:
        token = Token.objects.get(token=token, type=Token.TYPE_SIGN_IN_WITH_EMAIL)

        if token.is_expired():
            bad_request_error("Token has expired! Please request a new one")
        if not token.user.login_with_email:
            bad_request_error("Please enable login with email")

        token.delete()
        login(request, token.user)
        messages.success(request, "Signed in successfully")
        return redirect("my_account")
    except Token.DoesNotExist:
        messages.error(request, "Invalid token")
        return redirect("sign_in_with_email")
    except BadRequestError as e:
        messages.error(request, e.message)
        return redirect("sign_in_with_email")
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect("sign_in_with_email")


def sign_out(request):
    logout(request)
    return redirect("sign_in")


def verify_email(request: HttpRequest, token: str):
    user = request.user
    is_authenticated = user.is_authenticated
    redirect_url_name = (
        reverse_with_params("my_account", {"tab": "email"})
        if is_authenticated
        else "sign_in"
    )

    try:
        obj_token = Token.objects.get(token=token, type="email_verification")

        if is_authenticated and user != obj_token.user:
            bad_request_error("Invalid token")
        if obj_token.is_expired():
            bad_request_error("Token has expired! Please request a new one")
        if obj_token.user.email_verified:
            bad_request_error("Email has already been verified")

        obj_token.user.email_verified = True
        obj_token.user.save()
        obj_token.delete()
        messages.success(request, "Email verified successfully")
        return redirect(redirect_url_name)
    except Token.DoesNotExist:
        messages.error(request, "Invalid token")
        return redirect(redirect_url_name)
    except BadRequestError as e:
        messages.error(request, e.message)
        return redirect(redirect_url_name)
    except Exception as e:
        messages.error(request, f"Error verifying email: {e}")
        return redirect(redirect_url_name)


def forgot_password(request: HttpRequest):
    if request.method != "POST":
        return render(request, "forgot_password.html")

    email = request.POST.get("email", "")

    try:
        if not validate([email]):
            bad_request_error("Please fill in all fields")

        user = User.objects.get(email=email)
        send_password_reset_email.delay_on_commit(user.id)
        messages.success(request, "Password reset email sent successfully")
        return redirect("my_account" if user.is_authenticated else "sign_in")
    except User.DoesNotExist:
        messages.error(request, "User does not exist")
        return redirect("forgot_password")
    except BadRequestError as e:
        messages.error(request, e.message)
        return redirect("forgot_password")
    except Exception as e:
        messages.error(request, f"Error sending password reset email: {e}")
        return redirect("forgot_password")


def reset_password(request: HttpRequest, token: str):
    if request.method != "POST":
        return render(request, "reset_password.html", {"token": token})

    password = request.POST.get("password", "")
    confirm_password = request.POST.get("confirm_password", "")

    try:
        if not validate([password, confirm_password]):
            bad_request_error("Please fill in all fields")
        if password.strip() != confirm_password.strip():
            bad_request_error("Passwords do not match")

        password_id_valid = validate_password(password)
        if not password_id_valid[0]:
            bad_request_error(password_id_valid[1])

        obj_token = Token.objects.get(token=token, type=Token.TYPE_PASSWORD_RESET)

        if obj_token.is_expired():
            bad_request_error(
                "Token has expired! Please request a new one",
                "forgot_password",
            )

        user = obj_token.user
        user.set_password(password)
        user.save()
        obj_token.delete()
        send_password_changed_email.delay_on_commit(user.id)
        messages.success(request, "Password reset successfully")
        return redirect("sign_in")
    except Token.DoesNotExist:
        messages.error(request, "Invalid token")
        return redirect("forgot_password")
    except BadRequestError as e:
        messages.error(request, e.message)
        redirect_url = e.redirect_url or "reset_password"
        kwargs = {"token": token} if redirect_url == "reset_password" else {}
        return redirect(redirect_url, **kwargs)
    except Exception as e:
        messages.error(request, f"Error resetting password: {e}")
        return redirect("forgot_password")
