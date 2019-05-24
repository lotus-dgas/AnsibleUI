"""AnsibleUI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from public.viewFunc.ansibleIndex import *
from decorators import *

from django.views.generic.base import RedirectView
from public.views import Index

urlpatterns = [
    path('tasks/', tasks),
    re_path('opt_task/', ProxyAuth(AnsibleTask.as_view())),
    # path(r'(?P<dataName>\w+)/(?P<dataKey>\w+)', ProxyAuth(AnsibleAjax.as_view())),
    # re_path(r'(?P<dataName>\w+)', ProxyAuth(AnsibleAjax.as_view())),    # groups， tasks，funcs
    re_path(r'(?P<dataName>\w+)/(?P<dataKey>\w+)', ProxyAuth(AnsibleRequestApi.as_view())),
    re_path(r'(?P<dataName>\w+)', ProxyAuth(AnsibleRequestApi.as_view())),    # groups， tasks，funcs
    path('', Index.as_view()),
]
