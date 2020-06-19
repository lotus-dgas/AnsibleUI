
#coding: utf8
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
import json, datetime, redis, os, random, string, ast
from myCelery import ansiblePlayBook_v2, ansibleExec, syncAnsibleResult
from tools.config import REDIS_ADDR, REDIS_PORT, REDIS_PD, ansible_result_redis_db
from public.templatetags.custom_markdown import ansible_result
# from django.core.cache import caches
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from tools.AnsibleModules import data as ansible_modules_gather
from public.models import *
from decorators.Proxy import ProxyAuth
import logging
logger = logging.getLogger('ansible.ui')

from myCelery import appCelery

class CeleryControl:
    def __init__(self):
        self.c = appCelery.control.inspect()

    # 增加 pool 
    def grow(self, nodeName, num):
        return appCelery.control.pool_grow(n=num, reply=True, destination=[nodeName])

class CeleyWorker(View):
    def get(self, request, *a, **kw):
        if kw.get('name'):
            name = kw.get('name')
            i = appCelery.control.inspect()
            data = i.stats()
            return render(request, kw.get('template_file', None) or 'public/celery_detail.html', {'data': data.get(name)})
        i = appCelery.control.inspect()
        data = i.stats()
        return render(request, kw.get('template_file', None) or 'public/celery.html', {'data': data})

    # 控制增减celery worker 数目
    def post(self, request, *a,  **kw):
        data = request.POST.dict()
        if data.get('opt', '') == 'grow':
            num = int(data.get('num', '0'))
            node_name = data.get('node_name', None)
            if num and node_name:
                ret = appCelery.control.pool_grow(n=num, reply=True, destination=[node_name])
                print(ret)
                return JsonResponse({'data': ret, 'msg': '%s: %s'% (node_name, ret[0][node_name])})
        elif data.get('opt', '') == 'shrink':
            num = int(data.get('num', '0'))
            node_name = data.get('node_name', None)
            if num and node_name:
                ret = appCelery.control.pool_shrink(n=num, reply=True, destination=[node_name])
                return JsonResponse({'data': ret, 'msg': '%s: %s'% (node_name, ret[0][node_name])})
        return JsonResponse({'msg': 'ok'})



