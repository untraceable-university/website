from django.urls import path

from . import views

urlpatterns = [
    path("", views.index),
    path("join/<slug:slug>/", views.join_us, name="join_us"),
    path("join/", views.join_us, name="join_us"),
    path("research/", views.page, { "slug": "research" }, name="research"),
    path("teaching/", views.page, { "slug": "teaching" }, name="teaching"),
    path("overview/", views.page, { "slug": "overview" }, name="overview"),
    path("timeline/", views.page, { "slug": "timeline" }, name="timeline"),
    path("contact/", views.contact, name="contact"),
    path("templates/", views.templates),
]
