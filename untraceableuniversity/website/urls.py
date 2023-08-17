from django.urls import path

from . import views

urlpatterns = [
    path("", views.index),
    path("join/<slug:slug>/", views.join_us),
]
