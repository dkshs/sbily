from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import redirect
from django.shortcuts import render

from sbily.links.models import ShortenedLink
from sbily.users.models import User

from .utils import validate

MIN_PASSWORD_LENGTH = 8


ADMIN_URL = f"{settings.BASE_URL}{settings.ADMIN_URL}"


def sign_up(request):  # noqa: PLR0911
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        first_name = request.POST.get("first_name") or ""
        last_name = request.POST.get("last_name") or ""
        username = request.POST.get("username") or ""
        email = request.POST.get("email") or ""
        password = request.POST.get("password") or ""
        if not validate([username, email, password]):
            messages.error(request, "Please fill in all fields")
            return redirect("sign_up")
        if len(password.strip()) < MIN_PASSWORD_LENGTH:
            messages.error(
                request,
                f"Password must be at least {MIN_PASSWORD_LENGTH} characters",
            )
            return redirect("sign_up")
        if " " in password:
            messages.error(request, "Password cannot contain spaces")
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
            messages.success(request, "User created successfully")
            login(request, user)
            return redirect("home")
        except Exception as e:  # noqa: BLE001
            messages.error(request, f"Error creating user: {e}")
            return redirect("sign_up")
    return render(request, "sign_up.html")


def sign_in(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        username = request.POST.get("username") or ""
        password = request.POST.get("password") or ""
        if not validate([username, password]):
            messages.error(request, "Please fill in all fields")
            return redirect("sign_in")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        messages.error(request, "Invalid username or password")
        return redirect("sign_in")
    return render(request, "sign_in.html")


def sign_out(request):
    logout(request)
    return redirect("sign_in")


@login_required
def my_account(request: HttpRequest):
    user = request.user
    if request.method == "POST":
        first_name = request.POST.get("first_name") or ""
        last_name = request.POST.get("last_name") or ""
        username = request.POST.get("username") or ""
        email = request.POST.get("email") or ""
        if not validate([username]):
            messages.error(request, "Username is required")
            return redirect("my_account")
        if (
            user.username == username
            and user.email == email
            and user.first_name == first_name
            and user.last_name == last_name
        ):
            messages.warning(request, "There were no changes")
            return redirect("my_account")
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        user.save()
        messages.success(request, "User updated successfully")
    links = ShortenedLink.objects.filter(user=user).order_by("-updated_at")
    return render(
        request,
        "my_account.html",
        {"user": user, "links": links, "ADMIN_URL": ADMIN_URL},
    )


@login_required
def change_password(request: HttpRequest):
    if request.method == "POST":
        old_password = request.POST.get("old_password") or ""
        new_password = request.POST.get("new_password") or ""
        if not validate([old_password, new_password]):
            messages.error(request, "Please fill in all fields")
            return redirect("change_password")
        if len(new_password.strip()) < MIN_PASSWORD_LENGTH:
            messages.error(
                request,
                f"Password must be at least {MIN_PASSWORD_LENGTH} characters",
            )
            return redirect("change_password")
        if " " in new_password:
            messages.error(request, "Password cannot contain spaces")
            return redirect("change_password")
        if old_password.strip() == new_password.strip():
            messages.error(request, "The old and new password cannot be the same")
            return redirect("change_password")
        user = request.user
        if not user.check_password(old_password):
            messages.error(request, "The old password is incorrect")
            return redirect("change_password")
        user.set_password(new_password)
        user.save()
        messages.success(request, "Successful updated password")
    return render(request, "change_password.html")
