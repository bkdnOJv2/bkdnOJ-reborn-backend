from django.contrib import admin
from django.urls import path, include

from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from auth.views import UserList, UserDetail, GroupList, GroupDetail

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Token, Register, Password Change, ...
    path('', include('auth.urls')),

    # UserProfile
    path('', include('userprofile.urls')),
    # Organization
    path('', include('organization.urls')),
    # Organization
    path('', include('problem.urls')),
    # Judge
    path('', include('judger.restful.urls')),
    # Submission
    path('', include('submission.urls')),

    # Submission
    path('', include('compete.urls')),

    path('__debug__', include('debug_toolbar.urls')),

]

# urlpatterns = format_suffix_patterns(urlpatterns)
from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
