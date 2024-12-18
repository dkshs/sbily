from django.urls import include
from django.urls import path

from . import views

account_urlpatterns = [
    path("", views.my_account, name="my_account"),
    path("change_password", views.change_password, name="change_password"),
    path("delete_account", views.delete_account, name="delete_account"),
]

auth_urlpatterns = [
    path("sign_up/", views.sign_up, name="sign_up"),
    path("sign_in/", views.sign_in, name="sign_in"),
    path("sign_out/", views.sign_out, name="sign_out"),
    path("verify_email/<str:token>", views.verify_email, name="verify_email"),
    path("resend_verify_email/", views.resend_verify_email, name="resend_verify_email"),
]

urlpatterns = [
    path("me/", include(account_urlpatterns)),
    path("auth/", include(auth_urlpatterns)),
]
