from django.urls import path
from django.shortcuts import redirect

from . import views

urlpatterns = [
    path("", views.index, name="index"),

    path("activities/<slug:slug>/", views.page, name="activities"),
    path("activities/", views.page, {"slug": "activities"}, name="activities"),

    path("join/<slug:slug>/", views.page, name="join"),
    path("join/", views.page, {"slug": "join"}, name="join"),

    path("about/", views.page, { "slug": "about" }, name="about"),
    path("about/<slug:slug>/", views.page, name="about"),
    path("about/<slug:slug>/<slug:child_page>/", views.page, name="about"),

    path("video/", views.video, name="video"),
    path("contact/", views.contact, name="contact"),
    path("templates/", views.templates),

    path("terms-and-conditions/", views.page_simple, { "slug": "terms-and-conditions" }, name="terms-and-conditions"),

    # Control panel
    path("controlpanel/", views.controlpanel, name="controlpanel"),
    path("controlpanel/page/<int:id>/", views.controlpanel_page, name="controlpanel_page"),
    path("controlpanel/page/", views.controlpanel_page, name="controlpanel_page"),
    
    path("tac/", lambda request: redirect("/join/tac/")),
    path("cat/", lambda request: redirect("/es/join/tac/")),

    # Redirecting old URLs. Remove by June 2024:
    path("research/", lambda request: redirect("/activities/research/")),
    path("teaching/", lambda request: redirect("/activities/education-and-outreach/")),
    path("overview/", lambda request: redirect("/about/")),

]
