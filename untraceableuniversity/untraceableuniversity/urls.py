from django.contrib import admin
from django.urls import path, include
from website.admin import admin_site  
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path("admin/", admin_site.urls),
    path("mdeditor/", include("mdeditor.urls")),
]

urlpatterns += i18n_patterns(
    path("", include("website.urls")),
    prefix_default_language = False
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
