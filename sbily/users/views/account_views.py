# ruff: noqa: BLE001
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render

from sbily.users.tasks import send_deactivated_account_email
from sbily.users.tasks import send_email_verification
from sbily.users.tasks import send_password_changed_email
from sbily.utils.data import validate
from sbily.utils.data import validate_password
from sbily.utils.errors import BadRequestError
from sbily.utils.errors import bad_request_error

LINK_BASE_URL = getattr(settings, "LINK_BASE_URL", None)
ADMIN_URL = f"{settings.BASE_URL}{settings.ADMIN_URL}"


@login_required
def my_account(request: HttpRequest):
    if request.method != "POST":
        return render(request, "account/index.html")

    user = request.user
    first_name = request.POST.get("first_name", "").strip()
    last_name = request.POST.get("last_name", "").strip()
    username = request.POST.get("username", "").strip()

    try:
        if not validate([username]):
            bad_request_error("Username are required!")

        if not any(
            [
                user.username != username,
                user.first_name != first_name,
                user.last_name != last_name,
            ],
        ):
            messages.warning(request, "There were no changes")
            return redirect("my_account")

        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.save()
        messages.success(request, "Successfully updated profile")
        return redirect("my_account")
    except BadRequestError as e:
        messages.error(request, e.message)
        return redirect("my_account")
    except Exception as e:
        messages.error(request, f"Error updating profile: {e}")
        return redirect("my_account")


@login_required
def account_email(request: HttpRequest):
    return render(request, "account/email.html")


@login_required
def account_security(request: HttpRequest):
    return render(request, "account/security.html")


@login_required
def links(request: HttpRequest):
    return render(request, "account/links.html")


@login_required
def change_password(request: HttpRequest):
    if request.method != "POST":
        return redirect("my_account")

    old_password = request.POST.get("old_password") or ""
    new_password = request.POST.get("new_password") or ""

    try:
        if not validate([old_password, new_password]):
            bad_request_error("Please fill in all fields")
        if old_password.strip() == new_password.strip():
            bad_request_error("The old and new password cannot be the same")

        password_id_valid = validate_password(new_password)
        if not password_id_valid[0]:
            bad_request_error(password_id_valid[1])

        user = request.user
        if not user.email_verified:
            bad_request_error("Please verify your email first")
        if not user.check_password(old_password):
            bad_request_error("The old password is incorrect")

        user.set_password(new_password)
        user.save()
        send_password_changed_email.delay_on_commit(request.user.id)
        messages.success(request, "Successful updated password! Please re-login")
        return redirect("my_account")
    except BadRequestError as e:
        messages.error(request, e.message)
        return redirect("my_account")
    except Exception as e:
        messages.error(request, f"Error updating password: {e}")
        return redirect("my_account")


@login_required
def resend_verify_email(request: HttpRequest):
    try:
        user = request.user
        if user.email_verified:
            bad_request_error("Email has already been verified")
        send_email_verification.delay_on_commit(user.id)
        messages.success(request, "Verification email sent successfully")
        return redirect("account_email")
    except BadRequestError as e:
        messages.error(request, e.message)
        return redirect("account_email")
    except Exception as e:
        messages.error(request, f"Error sending verification email: {e}")
        return redirect("account_email")


@login_required
def deactivate_account(request: HttpRequest):
    try:
        user = request.user
        if not user.email_verified:
            bad_request_error("Please verify your email first")
        user.is_active = False
        user.save()
        send_deactivated_account_email.delay_on_commit(user.id)
        messages.success(request, "Account deactivate successfully")
        return redirect("sign_in")
    except BadRequestError as e:
        messages.error(request, e.message)
        return redirect("my_account")
    except Exception as e:
        messages.error(request, f"Error deactivating account: {e}")
        return redirect("my_account")


def set_user_timezone(request: HttpRequest):
    if "timezone" in request.POST:
        request.session["user_timezone"] = request.POST["timezone"]
    return JsonResponse({"status": "ok"})
