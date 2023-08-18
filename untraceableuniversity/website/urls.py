from django.urls import path

from . import views

urlpatterns = [
    path("", views.index),
    path("join/<slug:slug>/", views.join_us, name="join_us"),
    path("join/", views.join_us, name="join_us"),
    path("mission/", views.page, { "slug": "mission" }, name="mission"),
]
