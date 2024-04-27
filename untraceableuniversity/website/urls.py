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

    path("contact/", views.contact, name="contact"),
    path("templates/", views.templates),

    # Control panel
    path("controlpanel/", views.controlpanel, name="controlpanel"),
    path("controlpanel/page/<int:id>/", views.controlpanel_page, name="controlpanel_page"),
    path("controlpanel/page/", views.controlpanel_page, name="controlpanel_page"),

    # Redirecting old URLs. Remove by June 2024:
    path("research/", lambda request: redirect("/activities/research/")),
    path("teaching/", lambda request: redirect("/activities/education-and-outreach/")),

]
