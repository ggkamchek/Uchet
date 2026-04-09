from django.contrib import admin
from django.urls import path, include
from main import views as main_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', main_views.role_redirect, name='root'),
    path('admin/', admin.site.urls),
    path('dashboard/', include('main.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
