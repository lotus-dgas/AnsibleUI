"""AnsibleUI URL Configuration
"""
from django.contrib import admin
from django.urls import path, re_path
from public.viewFunc.ansibleIndex import *
from decorators import *

from django.views.generic.base import RedirectView
from public.views import Index
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('tasks/', tasks),
    re_path('opt_task/', ProxyAuth(AnsibleTask.as_view())),
    re_path('opt_task_api/', csrf_exempt(AnsibleTaskApi.as_view())),
    # path(r'(?P<dataName>\w+)/(?P<dataKey>\w+)', ProxyAuth(AnsibleAjax.as_view())),
    # re_path(r'(?P<dataName>\w+)', ProxyAuth(AnsibleAjax.as_view())),    # groups， tasks，funcs
    re_path(r'(?P<dataName>\w+)/(?P<dataKey>\w+)', ProxyAuth(AnsibleRequestApi.as_view())),
    re_path(r'(?P<dataName>\w+)', ProxyAuth(AnsibleRequestApi.as_view())),    # groups， tasks，funcs
    path('', Index.as_view()),
]
