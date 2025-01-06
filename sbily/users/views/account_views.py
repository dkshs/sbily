# ruff: noqa: BLE001
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import redirect
from django.shortcuts import render

from sbily.links.models import ShortenedLink
from sbily.users.tasks import send_email_verification
from sbily.users.tasks import send_password_changed_email
from sbily.utils.data import validate
from sbily.utils.data import validate_password

LINK_BASE_URL = getattr(settings, "LINK_BASE_URL", None)
ADMIN_URL = f"{settings.BASE_URL}{settings.ADMIN_URL}"


@login_required
def my_account(request: HttpRequest):
    user = request.user
    if request.method == "POST":
        first_name = request.POST.get("first_name") or ""
        last_name = request.POST.get("last_name") or ""
        username = request.POST.get("username") or ""
        email = request.POST.get("email") or ""
        login_with_email = request.POST.get("login_with_email") == "on"
        if not validate([username, email]):
            messages.error(request, "Username and email are required")
            return redirect("my_account")
        if (
            user.username == username
            and user.email == email
            and user.first_name == first_name
            and user.last_name == last_name
            and user.login_with_email == login_with_email
        ):
            messages.warning(request, "There were no changes")
            return redirect("my_account")
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        user.login_with_email = login_with_email
        user.save()
        messages.success(request, "User updated successfully")
    links = ShortenedLink.objects.filter(user=user).order_by("-updated_at")
    return render(
        request,
        "my_account.html",
        {
            "user": user,
            "links": links,
            "ADMIN_URL": ADMIN_URL,
            "LINK_BASE_URL": LINK_BASE_URL,
        },
    )


@login_required
def change_password(request: HttpRequest):  # noqa: PLR0911
    if request.method != "POST":
        return render(request, "change_password.html")

    old_password = request.POST.get("old_password") or ""
    new_password = request.POST.get("new_password") or ""

    if not validate([old_password, new_password]):
        messages.error(request, "Please fill in all fields")
        return redirect("change_password")
    if old_password.strip() == new_password.strip():
        messages.error(request, "The old and new password cannot be the same")
        return redirect("change_password")

    password_id_valid = validate_password(new_password)
    if not password_id_valid[0]:
        messages.error(request, password_id_valid[1])
        return redirect("change_password")

    user = request.user
    if not user.email_verified:
        messages.error(request, "Please verify your email first")
        return redirect("change_password")
    if not user.check_password(old_password):
        messages.error(request, "The old password is incorrect")
        return redirect("change_password")

    user.set_password(new_password)
    user.save()
    send_password_changed_email.delay_on_commit(request.user.id)
    messages.success(request, "Successful updated password! Please re-login")
    return redirect("my_account")


@login_required
def resend_verify_email(request: HttpRequest):
    try:
        user = request.user
        if user.email_verified:
            messages.warning(request, "Email has already been verified")
            return redirect("my_account")
        send_email_verification.delay_on_commit(user.id)
        messages.success(request, "Verification email sent successfully")
        return redirect("my_account")
    except Exception as e:
        messages.error(request, f"Error sending verification email: {e}")
        return redirect("my_account")


@login_required
def delete_account(request: HttpRequest):
    if not request.user.email_verified:
        messages.error(request, "Please verify your email first")
        return redirect("my_account")
    request.user.delete()
    messages.success(request, "User deleted successfully")
    return redirect("sign_in")
