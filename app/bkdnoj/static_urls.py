from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from django.views.generic.base import RedirectView

REACT_APP_STATIC_FILES = ["asset-manifest.json", "favicon.ico", "logo192.png", "logo512.png", "manifest.json", "robots.txt"]

urlpatterns = [
    path(fname, RedirectView.as_view(url='/static/'+fname, permanent=True)) for fname in REACT_APP_STATIC_FILES
]

