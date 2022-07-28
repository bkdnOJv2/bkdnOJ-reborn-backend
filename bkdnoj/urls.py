from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from auth.views import UserList, UserDetail, GroupList, GroupDetail
from django.views.generic import TemplateView

urlpatterns = [
    path('', include('bkdnoj.static_urls')),
    path('api/admin/', admin.site.urls),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Token, Register, Password Change, ...
    path('api/', include([
        path('', include('auth.urls')),
        path('', include('userprofile.urls')),
        path('', include('organization.urls')),
        path('', include('problem.urls')),
        path('', include('judger.restful.urls')),
        path('', include('submission.urls')),
        path('', include('compete.urls')),
    ])),
]

def loader_io(request):
    return HttpResponse('loaderio-e932291bca6cb4c5ef455de0ed45c6ed', content_type="text/plain")
urlpatterns += [path('__debug__', include('debug_toolbar.urls'))]
urlpatterns += [path('loaderio-e932291bca6cb4c5ef455de0ed45c6ed/', loader_io, name='loader-io-view')]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += [
#     # ReactAPp
#     re_path(r'^(?!api/).*', TemplateView.as_view(template_name='index.html')),
# ]
