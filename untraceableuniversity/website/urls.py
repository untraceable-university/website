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

    # Redirects so we can use short URLs in brochures etc.
    path("tac/", lambda request: redirect("/join/tac/")),
    path("cat/", lambda request: redirect("/es/join/tac/")),

    # Control panel
    path("controlpanel/", views.controlpanel, name="controlpanel"),
    path("controlpanel/pages/", views.controlpanel_pages, name="controlpanel_pages"),
    path("controlpanel/pages/<int:id>/", views.controlpanel_page, name="controlpanel_page"),
    path("controlpanel/pages/create/", views.controlpanel_page, name="controlpanel_page"),

    path("controlpanel/links/", views.controlpanel_links, name="controlpanel_links"),
    path("controlpanel/links/<int:id>/", views.controlpanel_link, name="controlpanel_link"),
    path("controlpanel/links/create/", views.controlpanel_link, name="controlpanel_link"),

    path("controlpanel/tags/", views.controlpanel_tags, name="controlpanel_tags"),
    path("controlpanel/tags/<int:id>/", views.controlpanel_tag, name="controlpanel_tag"),
    path("controlpanel/tags/create/", views.controlpanel_tag, name="controlpanel_tag"),

    path("controlpanel/people/", views.controlpanel_people_list, name="controlpanel_people_list"),
    path("controlpanel/people/<int:id>/", views.controlpanel_people, name="controlpanel_people"),
    path("controlpanel/people/create/", views.controlpanel_people, name="controlpanel_people"),

    path("controlpanel/meetings/", views.controlpanel_events, {"event_type": "meeting"}, name="controlpanel_meetings"),
    path("controlpanel/meetings/<int:id>/", views.controlpanel_event, name="controlpanel_meeting"),
    path("controlpanel/meetings/create/", views.controlpanel_event, name="controlpanel_meeting"),

    path("controlpanel/organizations/", views.controlpanel_organizations, name="controlpanel_organizations"),
    path("controlpanel/organizations/<int:id>/", views.controlpanel_organization, name="controlpanel_organization"),
    path("controlpanel/organizations/create/", views.controlpanel_organization, name="controlpanel_organization"),

]
