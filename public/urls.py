"""ansible_ui URL Configuration
"""
from django.urls import path, re_path
from public.views import *
from public.viewFunc.celeryIndex import CeleyWorker

urlpatterns = [
    # path('tasks/', tasks),

    # celery worker
    path('celery', CeleyWorker.as_view()),
    path('celery/<str:name>', CeleyWorker.as_view()),

    # 主机、服务器列表
    path('host/', HostsList.as_view(), name='hostsList'),
    path('host/<int:pk>/', HostsDetail.as_view(), name='hostsDetail'),

    # 项目组列表
    path('group/', GroupsList.as_view(), name='GroupsList'),
    path('group/<int:pk>/', GroupsDetail.as_view(), name='GroupsDetail'),

    # playbook 列表
    path('playbook/', PlaybookList.as_view(), name='PlaybookList'),
    path('playbook/<int:pk>/', PlaybookDetail.as_view(), name='PlaybookDetail'),

    # ansbile task 列表
    path('task/', AnsibleTaskList.as_view(), name='AnsibleTaskList'),
    path('task/<int:pk>/', AnsibleTaskDetail.as_view(), name='AnsibleTaskDetail'),

    # 添加任务页面/
    re_path('edit_task', TemplateReturn.as_view(), {'template_file':'public/edit_pb_task.html'}, name='EditPBTask'),

    # 提交任务地址
    re_path('opt_task/', AnsibleTask.as_view()),
    # re_path('opt_task_api/', csrf_exempt(AnsibleTaskApi.as_view())),    # csrf 豁免

    # re_path(r'(?P<dataName>\w+)/(?P<dataKey>\w+)', ProxyAuth(AnsibleRequestApi.as_view())),
    # re_path(r'(?P<dataName>\w+)', ProxyAuth(AnsibleRequestApi.as_view())),

    # 默认首页
    path('', Index.as_view()),
]
