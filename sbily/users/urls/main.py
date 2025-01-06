from django.urls import include
from django.urls import path

from .account import account_urlpatterns
from .auth import auth_urlpatterns

urlpatterns = [
    path("account/", include(account_urlpatterns)),
    path("auth/", include(auth_urlpatterns)),
]
