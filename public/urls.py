"""ansible_ui URL Configuration
"""
from django.contrib import admin
from django.urls import path, re_path
from public.viewFunc.ansibleIndex import *
from decorators import *

from django.views.generic.base import RedirectView
from public.views import Index

from public.viewFunc.ansibleExtra import AnsibleTaskApi
from django.views.decorators.csrf import csrf_exempt
from public.viewFunc.celeryIndex import CeleyWorker


urlpatterns = [
    path('tasks/', tasks),
    path('celery', CeleyWorker.as_view()),
    re_path('opt_task/', ProxyAuth(AnsibleTask.as_view())),

    re_path('opt_task_api/', csrf_exempt(AnsibleTaskApi.as_view())),    # csrf 豁免

    re_path(r'(?P<dataName>\w+)/(?P<dataKey>\w+)', ProxyAuth(AnsibleRequestApi.as_view())),
    re_path(r'(?P<dataName>\w+)', ProxyAuth(AnsibleRequestApi.as_view())),
    path('', Index.as_view()),
]
