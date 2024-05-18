# ruff: noqa: BLE001
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render

from .models import ShortenedLink
from .utils import link_is_valid

BASE_URL = getattr(settings, "BASE_URL", None)


@login_required
def home(request):
    return render(request, "home.html", {"BASE_URL": BASE_URL})


@login_required
def link(request, shortened_link):
    try:
        link = ShortenedLink.objects.get(shortened_link=shortened_link)
        return render(request, "link.html", {"link": link})
    except ShortenedLink.DoesNotExist:
        messages.error(request, "Link not found")
        return redirect("home")
    except Exception:
        messages.error(request, "An error occurred")
        return redirect("home")


@login_required
def create_link(request):
    if request.method != "POST":
        return redirect("home")
    original_link = request.POST.get("original_link") or ""
    shortened_link = request.POST.get("shortened_link") or ""
    if not link_is_valid(request, original_link, shortened_link):
        return redirect("home")
    try:
        ShortenedLink.objects.create(
            original_link=original_link,
            shortened_link=shortened_link,
            user=request.user,
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
            return redirect("home")
        return redirect(link.original_link)
    except ShortenedLink.DoesNotExist:
        messages.error(request, "Link not found")
        return redirect("home")
    except Exception:
        messages.error(request, "An error occurred")
        return redirect("home")
