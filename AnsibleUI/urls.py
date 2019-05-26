"""AnsibleUI URL Configuration
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ansible/', include('public.urls'),),
    path('', RedirectView.as_view(url='/ansible/'))
]
