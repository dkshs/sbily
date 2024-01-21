from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings

from .models import ShortenedLink
from .utils import link_is_valid

BASE_URL = getattr(settings, "BASE_URL", None)


def home(request):
    return render(request, "home.html", {"BASE_URL": BASE_URL})


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


def create_link(request):
    if request.method != "POST":
        return redirect("home")
    original_link = request.POST.get("original_link") or ""
    shortened_link = request.POST.get("shortened_link") or ""
    if not link_is_valid(request, original_link, shortened_link):
        return redirect("home")
    try:
        ShortenedLink.objects.create(original_link=original_link, shortened_link=shortened_link)
        messages.success(request, "Link created successfully")
        return redirect("link", shortened_link=shortened_link)
    except Exception:
        messages.error(request, "An error occurred")
        return redirect("home")


def redirect_link(request, shortened_link):
    try:
        link = ShortenedLink.objects.get(shortened_link=shortened_link)
        return redirect(link.original_link)
    except ShortenedLink.DoesNotExist:
        messages.error(request, "Link not found")
        return redirect("home")
    except Exception:
        messages.error(request, "An error occurred")
        return redirect("home")
