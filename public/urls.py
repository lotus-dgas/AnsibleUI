"""ansible_ui URL Configuration
"""
from django.contrib import admin
from django.urls import path, re_path
from public.viewFunc.ansibleIndex import *
from decorators import *

from django.views.generic.base import RedirectView
from public.views import *

from public.viewFunc.ansibleExtra import AnsibleTaskApi
from django.views.decorators.csrf import csrf_exempt
from public.viewFunc.celeryIndex import CeleyWorker

urlpatterns = [
    path('tasks/', tasks),
    path('celery', CeleyWorker.as_view()),
    path('celery/<str:name>', CeleyWorker.as_view()),
    re_path('opt_task/', ProxyAuth(AnsibleTask.as_view())),

    re_path('opt_task_api/', csrf_exempt(AnsibleTaskApi.as_view())),    # csrf 豁免

    path('host/', HostsList.as_view(), name='hostsList'),
    path('host/<int:pk>/', HostsDetail.as_view(), name='hostsDetail'),

    path('group/', GroupsList.as_view(), name='GroupsList'),
    path('group/<int:pk>/', GroupsDetail.as_view(), name='GroupsDetail'),

    path('playbook/', PlaybookList.as_view(), name='PlaybookList'),
    path('playbook/<int:pk>/', PlaybookDetail.as_view(), name='PlaybookDetail'),

    path('task/', AnsibleTaskList.as_view(), name='AnsibleTaskList'),
    path('task/<int:pk>/', AnsibleTaskDetail.as_view(), name='AnsibleTaskDetail'),

    re_path('edit_task', TemplateReturn.as_view(), {'template_file':'public/edit_pb_task.html'}, name='EditPBTask'),

    re_path(r'(?P<dataName>\w+)/(?P<dataKey>\w+)', ProxyAuth(AnsibleRequestApi.as_view())),
    re_path(r'(?P<dataName>\w+)', ProxyAuth(AnsibleRequestApi.as_view())),
    path('', Index.as_view()),
]
