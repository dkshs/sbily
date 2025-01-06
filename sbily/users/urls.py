from django.urls import include
from django.urls import path

from . import views

account_urlpatterns = [
    path("me/", views.my_account, name="my_account"),
    path("change_password/", views.change_password, name="change_password"),
    path("delete/", views.delete_account, name="delete_account"),
]

auth_sign_in_urlpatterns = [
    path("", views.sign_in, name="sign_in"),
    path("with_email/", views.sign_in_with_email, name="sign_in_with_email"),
    path(
        "with_email/<str:token>/",
        views.sign_in_with_email_verify,
        name="sign_in_with_email_verify",
    ),
]

auth_urlpatterns = [
    path("sign_up/", views.sign_up, name="sign_up"),
    path("sign_in/", include(auth_sign_in_urlpatterns)),
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
