"""LWH URL Configuration"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.v1.urls')),

    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]

# For production: serve React app
if not settings.DEBUG:
    # Let React handle all other routes
    urlpatterns.append(
        re_path(r'^.*', TemplateView.as_view(template_name='index.html')),
    )
# For development: add Django Debug Toolbar
else:
    try:
        import debug_toolbar
        urlpatterns.append(
            path('__debug__/', include(debug_toolbar.urls)),
        )
    except ImportError:
        pass