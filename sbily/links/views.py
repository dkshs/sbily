# ruff: noqa: BLE001
from datetime import UTC
from datetime import datetime
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render

from .models import ShortenedLink
from .utils import can_user_create_link
from .utils import link_is_valid

BASE_URL = getattr(settings, "BASE_URL", None)


@login_required
def home(request):
    return render(request, "home.html", {"BASE_URL": BASE_URL})


@login_required
def create_link(request):
    if request.method != "POST" or not can_user_create_link(request):
        return redirect("home")
    original_link = request.POST.get("original_link") or ""
    shortened_link = request.POST.get("shortened_link") or ""
    is_temporary = request.POST.get("is_temporary") == "on" or False
    if not link_is_valid(request, original_link, shortened_link):
        return redirect("home")
    try:
        ShortenedLink.objects.create(
            original_link=original_link,
            shortened_link=shortened_link,
            user=request.user,
            remove_at=datetime.now(UTC) + timedelta(days=1) if is_temporary else None,
        )
        messages.success(request, "Link created successfully")
        return redirect("link", shortened_link=shortened_link)
    except Exception:
        messages.error(request, "An error occurred")
        return redirect("home")


def redirect_link(request, shortened_link):
    try:
        link = ShortenedLink.objects.get(shortened_link=shortened_link)
        if not link.is_active:
            messages.error(request, "Link is not active")
            if request.user == link.user:
                return redirect("link", link.shortened_link)
            return redirect("home")
        return redirect(link.original_link)
    except ShortenedLink.DoesNotExist:
        messages.error(request, "Link not found")
        return redirect("home")
    except Exception:
        messages.error(request, "An error occurred")
        return redirect("home")


@login_required
def link(request, shortened_link):
    try:
        link = ShortenedLink.objects.get(
            shortened_link=shortened_link,
            user=request.user,
        )

        deactivate = request.GET.get("deactivate")
        if deactivate is not None:
            deactivate = deactivate == "True" or False
            link.is_active = not deactivate
            link.save()
            messages.success(
                request,
                f"Link {'deactivated' if deactivate else 'activated'}",
            )
            return redirect("my_account")

        return render(request, "link.html", {"link": link, "BASE_URL": BASE_URL})
    except ShortenedLink.DoesNotExist:
        messages.error(request, "Link not found")
        return redirect("home")
    except Exception:
        messages.error(request, "An error occurred")
        return redirect("home")


@login_required
def update_link(request, shortened_link):
    try:
        if request.method != "POST":
            return redirect("my_account")

        link = ShortenedLink.objects.get(
            shortened_link=shortened_link,
            user=request.user,
        )
        original_link = request.POST.get("original_link") or ""
        shortened_link = request.POST.get("shortened_link") or ""
        is_active = request.POST.get("is_active") == "on" or False
        is_temporary = request.POST.get("is_temporary") == "on" or False

        if not link_is_valid(request, original_link, shortened_link, link.id):
            return redirect("link", link.shortened_link)

        if (
            original_link == link.original_link
            and shortened_link == link.shortened_link
            and (is_active and link.is_active)
            and (is_temporary and link.remove_at is not None)
        ):
            messages.warning(request, "No changes were made")
            return redirect("link", link.shortened_link)

        link.original_link = original_link
        link.shortened_link = shortened_link
        link.is_active = is_active
        link.updated_at.now()
        link.remove_at = datetime.now(UTC) + timedelta(days=1) if is_temporary else None
        link.save()

        messages.success(request, "Link updated successfully")
        return redirect("link", link.shortened_link)
    except ShortenedLink.DoesNotExist:
        messages.error(request, "Link not found")
        return redirect("my_account")
    except Exception:
        messages.error(request, "An error occurred")
        return redirect("home")


@login_required
def delete_link(request, shortened_link):
    try:
        link = ShortenedLink.objects.get(
            shortened_link=shortened_link,
            user=request.user,
        )
        link.delete()
        messages.success(request, "Link deleted successfully")
        return redirect("my_account")
    except ShortenedLink.DoesNotExist:
        messages.error(request, "Link not found")
        return redirect("my_account")
    except Exception:
        messages.error(request, "An error occurred")
        return redirect("home")
