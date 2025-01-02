from django.urls import include
from django.urls import path
from django.urls import re_path

from . import views

account_urlpatterns = [
    path("me/", views.my_account, name="my_account"),
    path("change_password/", views.change_password, name="change_password"),
    path("delete/", views.delete_account, name="delete_account"),
]

auth_urlpatterns = [
    path("sign_up/", views.sign_up, name="sign_up"),
    path("sign_in/", views.sign_in, name="sign_in"),
    re_path(
        r"^sign_in_with_email(?:/(?P<token>[^/]+))?/$",
        views.sign_in_with_email,
        name="sign_in_with_email",
    ),
    path("sign_out/", views.sign_out, name="sign_out"),
    path("verify_email/<str:token>/", views.verify_email, name="verify_email"),
    path("resend_verify_email/", views.resend_verify_email, name="resend_verify_email"),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
    path("reset_password/<str:token>/", views.reset_password, name="reset_password"),
]

urlpatterns = [
    path("account/", include(account_urlpatterns)),
    path("auth/", include(auth_urlpatterns)),
]
