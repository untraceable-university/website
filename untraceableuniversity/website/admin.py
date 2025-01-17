from django.contrib import admin
from .models import *
from django.contrib.admin import AdminSite

class MyAdminSite(AdminSite):
    # Text to put at the end of each page"s <title>.
    site_title = "Untraceable University Admin"

    # Text to put in each page"s <h1> (and above login form).
    site_header = "Untraceable University Admin"

    # Text to put at the top of the admin index page.
    index_title = "Untraceable University"
    enable_nav_sidebar = False

class ContentAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    list_filter = ["language"]
    list_display = ["title", "page", "slug", "language"]

class PageAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "parent_page", "position"]

admin_site = MyAdminSite()

admin_site.register(Language)
admin_site.register(Page, PageAdmin)
admin_site.register(PageContent, ContentAdmin)
admin_site.register(Inspiration)
admin_site.register(Discipline)
admin_site.register(Question)
admin_site.register(FAQ)
admin_site.register(Organization)
admin_site.register(People)
