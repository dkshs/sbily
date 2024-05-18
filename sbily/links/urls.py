from django.urls import include
from django.urls import path

from . import views

link_urlpatterns = [
    path("", views.link, name="link"),
    path("edit", views.edit_link, name="edit_link"),
]

urlpatterns = [
    path("", views.home, name="home"),
    path("create_link/", views.create_link, name="create_link"),
    path("link/<str:shortened_link>/", include(link_urlpatterns)),
    path("<str:shortened_link>/", views.redirect_link, name="redirect_link"),
]
