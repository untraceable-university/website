from django.contrib import admin
from django.urls import path, include
from website.admin import admin_site  
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin_site.urls),
    path("", include("website.urls")),
    path("mdeditor/", include("mdeditor.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
