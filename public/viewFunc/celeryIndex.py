#

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
from django.core.cache import cache
from tools.AnsibleModules import data as ansible_modules_gather
from public.models import *
from decorators.Proxy import ProxyAuth
import logging
logger = logging.getLogger('ansible.ui')

from myCelery import appCelery

class CeleyWorker(View):
    def get(self, request, *a, **kw):
        if kw.get('name'):
            name = kw.get('name')
            print(kw)
            i = appCelery.control.inspect()
            data = i.stats()
            return render(request, 'public/celery_detail.html', {'data': data.get(name)})
        i = appCelery.control.inspect()
        data = i.stats()
        return render(request, 'public/celery.html', {'data': data})


