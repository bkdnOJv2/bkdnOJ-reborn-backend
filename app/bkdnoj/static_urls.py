"""
    URLs for static files. Used to config serving built React app.
"""

from django.urls import path
from django.views.generic.base import RedirectView

REACT_APP_STATIC_FILES = [
    "asset-manifest.json",
    "favicon.ico",
    "logo192.png",
    "logo512.png",
    "manifest.json",
    "robots.txt"]

urlpatterns = [
    path(fname, RedirectView.as_view(url='/static/'+fname, permanent=True))
    for fname in REACT_APP_STATIC_FILES
]
