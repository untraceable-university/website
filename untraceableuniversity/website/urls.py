from django.urls import path
from django.shortcuts import redirect

from . import views

urlpatterns = [
    path("", views.index, name="index"),

    path("activities/<slug:slug>/", views.page, name="activities"),
    path("activities/", views.page, {"slug": "activities"}, name="activities"),

    path("join/<slug:slug>/", views.page),
    path("join/", views.page, {"slug": "join_us"}, name="join_us"),

    path("overview/", views.page, { "slug": "overview" }, name="overview"),
    path("timeline/", views.page, { "slug": "timeline" }, name="timeline"),
    path("sites/", views.page, { "slug": "sites" }, name="sites"),
    path("contact/", views.contact, name="contact"),
    path("templates/", views.templates),

    # Redirecting old URLs. Remove by June 2024:
    path("research/", lambda request: redirect("/activities/research/")),
    path("teaching/", lambda request: redirect("/activities/education-and-outreach/")),
]
