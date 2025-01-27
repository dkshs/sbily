from django.urls import path

from . import views

urlpatterns = [
    path("", views.my_notifications, name="my_notifications"),
    path("<int:notification_id>", views.my_notification, name="my_notification"),
    path("handle_read/<int:notification_id>", views.handle_read, name="handle_read"),
    path(
        "delete/<int:notification_id>",
        views.delete_notification,
        name="delete_notification",
    ),
    path("mark_all_as_read", views.mark_all_as_read, name="mark_all_as_read"),
    path("delete_all", views.delete_all, name="delete_all"),
]
