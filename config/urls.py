from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.conf.urls.i18n import set_language

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/set-language/', set_language, name='set_language'),
    path('accounts/', include('allauth.urls')),
    path('api/', include([
        path('worksheets/', include('apps.worksheets.api_urls')),
        path('submissions/', include('apps.submissions.api_urls')),
    ])),
    path('', include('apps.accounts.urls')),
    path('worksheets/', include('apps.worksheets.urls')),
    path('workbooks/', include('apps.workbooks.urls')),
    path('assignments/', include('apps.assignments.urls')),
    path('library/', include('apps.library.urls')),
    path('submissions/', include('apps.submissions.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
