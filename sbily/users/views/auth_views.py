# ruff: noqa: BLE001
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.http import HttpRequest
from django.shortcuts import redirect
from django.shortcuts import render

from sbily.users.models import Token
from sbily.users.models import User
from sbily.users.tasks import send_password_changed_email
from sbily.users.tasks import send_password_reset_email
from sbily.users.tasks import send_sign_in_with_email
from sbily.users.tasks import send_welcome_email
from sbily.utils.data import validate
from sbily.utils.data import validate_password


def sign_up(request):  # noqa: PLR0911
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        first_name = request.POST.get("first_name") or ""
        last_name = request.POST.get("last_name") or ""
        username = request.POST.get("username") or ""
        email = request.POST.get("email") or ""
        password = request.POST.get("password") or ""
        if not validate([username, email]):
            messages.error(request, "Please fill in all fields")
            return redirect("sign_up")
        password_id_valid = validate_password(password)
        if not password_id_valid[0]:
            messages.error(request, password_id_valid[1])
            return redirect("sign_up")
        if User.objects.filter(username=username).exists():
            messages.error(request, "User already exists")
            return redirect("sign_up")
        try:
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
        except Exception as e:
            messages.error(request, f"Error creating user: {e}")
            return redirect("sign_up")
    return render(request, "sign_up.html")


def sign_in(request: HttpRequest):
    next_param = request.GET.get("next") or None
    if request.user.is_authenticated:
        return redirect("my_account")
    if request.method == "POST":
        username = request.POST.get("username") or ""
        password = request.POST.get("password") or ""
        next_param = request.POST.get("next") or None
        if not validate([username, password]):
            messages.error(request, "Please fill in all fields")
            return redirect("sign_in")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(next_param if next_param != "None" else "my_account")
        messages.error(request, "Invalid username or password")
        return redirect("sign_in")
    return render(request, "sign_in.html", {"next_param": next_param})


def sign_in_with_email(request: HttpRequest):  # noqa: PLR0911
    if request.user.is_authenticated:
        return redirect("my_account")
    if request.method != "POST":
        return render(request, "sign_in_with_email.html")

    email = request.POST.get("email") or ""
    if not validate([email]):
        messages.error(request, "Please fill in all fields")
        return redirect("sign_in_with_email")

    try:
        user = User.objects.get(email=email)
        if not user.email_verified:
            messages.error(request, "Please verify your email first")
            return redirect("sign_in_with_email")
        if not user.login_with_email:
            messages.error(request, "Please enable login with email")
            return redirect("sign_in_with_email")

        send_sign_in_with_email.delay_on_commit(user.id)
        messages.success(request, "Please check your email for a sign in link")
        return redirect("sign_in")
    except User.DoesNotExist:
        messages.error(request, "User does not exist")
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
            messages.error(request, "Token has expired! Please request a new one")
            return redirect("sign_in_with_email")
        if not token.user.login_with_email:
            messages.error(request, "Please enable login with email")
            return redirect("sign_in_with_email")

        token.delete()
        login(request, token.user)
        messages.success(request, "Signed in successfully")
        return redirect("my_account")
    except Token.DoesNotExist:
        messages.error(request, "Invalid token")
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
    redirect_url_name = "my_account" if is_authenticated else "sign_in"

    try:
        obj_token = Token.objects.get(token=token, type="email_verification")
        if is_authenticated and user != obj_token.user:
            messages.error(request, "Invalid token")
            return redirect(redirect_url_name)
        if obj_token.is_expired():
            messages.error(request, "Token has expired! Please request a new one")
            return redirect(redirect_url_name)
        if obj_token.user.email_verified:
            messages.warning(request, "Email has already been verified")
            return redirect(redirect_url_name)
        obj_token.user.email_verified = True
        obj_token.user.save()
        obj_token.delete()
        messages.success(request, "Email verified successfully")
        return redirect(redirect_url_name)
    except Token.DoesNotExist:
        messages.error(request, "Invalid token")
        return redirect(redirect_url_name)
    except Exception as e:
        messages.error(request, f"Error verifying email: {e}")
        return redirect(redirect_url_name)


def forgot_password(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("my_account")
    if request.method == "POST":
        email = request.POST.get("email") or ""
        if not validate([email]):
            messages.error(request, "Please fill in all fields")
            return redirect("forgot_password")
        try:
            user = User.objects.get(email=email)
            send_password_reset_email.delay_on_commit(user.id)
            messages.success(request, "Password reset email sent successfully")
            return redirect("sign_in")
        except User.DoesNotExist:
            messages.error(request, "User does not exist")
            return redirect("forgot_password")
        except Exception as e:
            messages.error(request, f"Error sending password reset email: {e}")
            return redirect("forgot_password")
    return render(request, "forgot_password.html")


def reset_password(request: HttpRequest, token: str):  # noqa: PLR0911
    if request.user.is_authenticated:
        return redirect("my_account")
    if request.method != "POST":
        return render(request, "reset_password.html", {"token": token})

    password = request.POST.get("password") or ""
    confirm_password = request.POST.get("confirm_password") or ""

    if not validate([password, confirm_password]):
        messages.error(request, "Please fill in all fields")
        return redirect("reset_password", token=token)
    if password.strip() != confirm_password.strip():
        messages.error(request, "Passwords do not match")
        return redirect("reset_password", token=token)

    password_id_valid = validate_password(password)
    if not password_id_valid[0]:
        messages.error(request, password_id_valid[1])
        return redirect("reset_password", token=token)

    try:
        obj_token = Token.objects.get(token=token, type=Token.TYPE_PASSWORD_RESET)

        if obj_token.is_expired():
            messages.error(request, "Token has expired! Please request a new one")
            return redirect("forgot_password")

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
    except Exception as e:
        messages.error(request, f"Error resetting password: {e}")
        return redirect("forgot_password")
