from django.urls import path

from sbily.users.views import account_views as views

account_urlpatterns = [
    path("", views.my_account, name="my_account"),
    path("email/", views.account_email, name="account_email"),
    path("security/", views.account_security, name="account_security"),
    path("links/", views.links, name="links"),
    path("change_password/", views.change_password, name="change_password"),
    path("resend_verify_email/", views.resend_verify_email, name="resend_verify_email"),
    path("deactivate/", views.deactivate_account, name="deactivate_account"),
    path("set_timezone/", views.set_user_timezone, name="set_user_timezone"),
]
