"""ansible_ui URL Configuration
"""
import rest_framework
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic.base import RedirectView

from public.views import Index
from public.viewFunc.middle import zabbix_api, jenkins_api
from public.viewFunc.account import myLogin, myLogout, myApply, notes
from public.viewFunc.celeryIndex import CeleyWorker, CeleryControl

from django.views.generic.base import TemplateView

from public.viewFunc import api
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPICodec

# swagger api
schema_view = get_schema_view(
    title='API 接口首页',
    description='![](/static/images/wei_1_meitu_3.jpg)![](/static/images/al_1_meitu_4.jpg)',
    renderer_classes=[SwaggerUIRenderer, OpenAPICodec],
)

# django drf 路径
router = routers.DefaultRouter()
router.register(r'user', api.UserViewSet)
router.register(r'hosts', api.HostViewSet)
router.register(r'groups', api.ProjectViewSet)
router.register(r'playbooks', api.FunctionsViewSet)
router.register(r'ansible_tasks', api.AnsibleTasksViewSet)


class WS(TemplateView):
    template_name = 'public/websocker.html'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('ansible/', include('public.urls'),),

    path('notes/', notes),
    # re_path(r'notes/(?P<dataKey>\w+)', notes),

    # 操作 celery 相关 路径
    path('celery/node/', CeleyWorker.as_view(), {'template_file': 'public/celery_node.html'}),
    path('celery/node/<str:name>/', CeleyWorker.as_view(), {'template_file': 'public/celery_node_detail.html'}),
 
    path('middle/zabbix', zabbix_api, name='zabbix'),
    path('middle/jenkins', jenkins_api, name='jenkins'),

    # 登录，退出，注册 路径
    path('account/login', myLogin),
    path('account/logout', myLogout),
    path('account/apply', myApply),

    # path('ws/conn', WSConn),
    path('ws/', WS.as_view()),

    # drf 路径
    path('api/', include(router.urls), name='api'),
    path('doc_v1/', include_docs_urls(
        title='API 文档v1',
        description='<img src="/static/images/w_199.jpeg" width="200px"><img src="/static/images/a_199.jpeg" width="200px">')),
    path('doc_v2/', schema_view, name='API 文档v2'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),


    # 处理 favicon.ico 问题
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico')),
    # path('', RedirectView.as_view(url='/ansible/'))
    path('', Index.as_view())
]
