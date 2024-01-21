from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("create_link/", views.create_link, name="create_link"),
    path("link/<str:shortened_link>/", views.link, name="link"),
    path("<str:shortened_link>/", views.redirect_link, name="redirect_link"),
]
