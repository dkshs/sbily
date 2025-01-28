# ruff: noqa: BLE001

import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone

from sbily.utils.data import validate
from sbily.utils.urls import redirect_with_params

from .models import DeletedShortenedLink
from .models import ShortenedLink

LINK_BASE_URL = getattr(settings, "LINK_BASE_URL", None)
LINK_REMOVE_AT_EXCLUDE = r".\d*[-+]\d{2}:\d{2}"


def home(request: HttpRequest):
    return render(request, "home.html", {"LINK_BASE_URL": LINK_BASE_URL})


def create_link(request: HttpRequest):
    if request.method != "POST":
        return redirect("home")

    next_path = request.POST.get("next_path", "home")
    original_link = request.POST.get("original_link", "").strip()
    shortened_link = request.POST.get("shortened_link", "").strip()
    remove_at = request.POST.get("remove_at", "").strip()
    is_temporary = request.POST.get("is_temporary") == "on"

    if not validate([original_link]):
        messages.error(request, "Please enter a valid original link")
        return redirect(next_path)

    if not request.user.is_authenticated:
        return redirect_with_params("sign_in", {"original_link": original_link})

    try:
        link_data = {
            "original_link": original_link,
            "shortened_link": shortened_link,
            "user": request.user,
        }

        if is_temporary:
            link_data["remove_at"] = timezone.now() + ShortenedLink.DEFAULT_EXPIRY
        if remove_at:
            link_data["remove_at"] = timezone.datetime.fromisoformat(
                f"{remove_at}+00:00",
            )

        link = ShortenedLink.objects.create(**link_data)
        messages.success(request, "Link created successfully")
        return redirect("link", shortened_link=link.shortened_link)
    except ValidationError as e:
        messages.error(request, str(e.messages[0]))
        return redirect(next_path)
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect(next_path)


def redirect_link(request: HttpRequest, shortened_link: str):
    try:
        link = ShortenedLink.objects.get(shortened_link=shortened_link)
        if not link.is_functional():
            messages.error(request, "Link is expired or deactivated")
            if request.user == link.user:
                return redirect("link", link.shortened_link)
            return redirect("home")
        return redirect(link.original_link)
    except ShortenedLink.DoesNotExist:
        messages.error(request, "Link not found")
        return redirect("home")
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect("home")


@login_required
def link(request: HttpRequest, shortened_link: str):
    try:
        link = ShortenedLink.objects.get(
            shortened_link=shortened_link,
            user=request.user,
        )

        deactivate = request.GET.get("deactivate")
        if deactivate is not None:
            deactivate = deactivate.lower() == "true"
            link.is_active = not deactivate
            link.save(update_fields=["is_active"])
            messages.success(
                request,
                f"Link {'deactivated' if deactivate else 'activated'}",
            )
            return redirect("my_account")

        link_remove_at = re.sub(
            LINK_REMOVE_AT_EXCLUDE,
            "",
            f"{timezone.localtime(link.remove_at)}",
        )
        return render(
            request,
            "link.html",
            {
                "link": link,
                "link_remove_at": link_remove_at,
                "LINK_BASE_URL": LINK_BASE_URL,
            },
        )
    except ShortenedLink.DoesNotExist:
        messages.error(request, "Link not found")
        return redirect("my_account")
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect("my_account")


@login_required
def update_link(request: HttpRequest, shortened_link: str):
    if request.method != "POST":
        return redirect("my_account")

    old_shortened_link = shortened_link

    try:
        link = ShortenedLink.objects.select_for_update().get(
            shortened_link=shortened_link,
            user=request.user,
        )
        link.remove_at = re.sub(LINK_REMOVE_AT_EXCLUDE, "", f"{link.remove_at}")

        form_data = {
            "original_link": request.POST.get("original_link", "").strip(),
            "shortened_link": request.POST.get("shortened_link", "").strip(),
            "remove_at": request.POST.get("remove_at", "").strip(),
            "is_active": request.POST.get("is_active") == "on",
        }

        if not validate([form_data["original_link"]]):
            msg = "Please enter a valid original link"
            raise ValidationError(msg)  # noqa: TRY301

        if form_data["remove_at"]:
            form_data["remove_at"] = f"{form_data['remove_at'].replace('T', ' ')}"
        if (
            form_data["original_link"] == link.original_link
            and form_data["shortened_link"] == link.shortened_link
            and form_data["remove_at"] == str(link.remove_at)
            and form_data["is_active"] == link.is_active
        ):
            messages.warning(request, "No changes were made")
            return redirect("link", old_shortened_link)

        link.original_link = form_data["original_link"]
        link.shortened_link = form_data["shortened_link"]
        link.remove_at = None
        if form_data["remove_at"]:
            link.remove_at = timezone.datetime.fromisoformat(
                f"{form_data['remove_at']}+00:00",
            )
        link.is_active = form_data["is_active"]
        link.save()

        messages.success(request, "Link updated successfully")
        return redirect("link", link.shortened_link)
    except ShortenedLink.DoesNotExist:
        messages.error(request, "Link not found")
        return redirect("my_account")
    except ValidationError as e:
        messages.error(
            request,
            str(e) if isinstance(e.messages, str) else e.messages[0],
        )
        return redirect("link", old_shortened_link)
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect("my_account")


@login_required
def delete_link(request: HttpRequest, shortened_link: str):
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
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect("home")


@login_required
def deleted_links(request: HttpRequest):
    links = DeletedShortenedLink.objects.filter(user=request.user)
    return render(request, "deleted_links.html", {"links": links})


@login_required
def restore_link(request: HttpRequest, shortened_link: str):
    try:
        link = DeletedShortenedLink.objects.get(
            shortened_link=shortened_link,
            user=request.user,
        )
        link.restore()
        messages.success(request, "Link restored successfully")
        return redirect("deleted_links")
    except DeletedShortenedLink.DoesNotExist:
        messages.error(request, "Link deleted not found")
        return redirect("deleted_links")
    except ValidationError as e:
        messages.error(
            request,
            str(e) if isinstance(e.messages, str) else e.messages[0],
        )
        return redirect("deleted_links")
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect("deleted_links")


@login_required
def remove_deleted_link(request: HttpRequest, shortened_link: str):
    try:
        link = DeletedShortenedLink.objects.get(
            shortened_link=shortened_link,
            user=request.user,
        )

        link.delete()
        messages.success(request, "Link deleted successfully")
        return redirect("deleted_links")
    except DeletedShortenedLink.DoesNotExist:
        messages.error(request, "Link deleted not found")
        return redirect("deleted_links")
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect("deleted_links")


@login_required
def handle_link_actions(request: HttpRequest):
    if request.method != "POST":
        return redirect("my_account")

    user = request.user
    next_path = request.POST.get("next_path", "my_account")
    link_ids = request.POST.getlist("_selected_action")
    action = request.POST.get("action")

    filters = Q(id__in=link_ids, user=user)
    shortened_links = ShortenedLink.objects.filter(filters)
    deleted_links = DeletedShortenedLink.objects.filter(filters)

    actions = {
        "delete_selected": shortened_links.delete,
        "activate_selected": shortened_links.update,
        "deactivate_selected": shortened_links.update,
        "restore_selected": deleted_links.restore,
        "delete_selected_deleted_links": deleted_links.delete,
    }

    if not action or action not in actions:
        messages.error(request, "Invalid action")
        return redirect(next_path)
    if not link_ids:
        messages.error(request, "No links selected")
        return redirect(next_path)

    try:
        if action in ("activate_selected", "deactivate_selected"):
            actions[action](is_active=action == "activate_selected")
        else:
            actions[action]()
        messages.success(request, f"Links {action.split('_')[0]}d successfully")
    except ValidationError as e:
        messages.error(
            request,
            str(e) if isinstance(e.messages, str) else e.messages[0],
        )
        return redirect(next_path)
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect(next_path)
    return redirect(next_path)
