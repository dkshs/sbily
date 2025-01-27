from django import template

from sbily.notifications.models import Notification

register = template.Library()


@register.filter
def get_notification_color(value: str) -> str:
    if value == Notification.SUCCESS:
        return "green-600"
    if value == Notification.WARNING:
        return "yellow-600"
    if value == Notification.ERROR:
        return "red-600"
    return "blue-600"
