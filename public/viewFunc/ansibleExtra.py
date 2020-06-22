#coding: utf8
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
import json, datetime, redis, os
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


# def ansible_result_analyze_jenkins(s):
#     if not s:
#         return "未搜索🔍到结果"
#     data = json.loads(s)
#     msg = ""
#     for d in data:
#         if  d.get('status') in [ "failed", "unreachable" ]:
#             msg += '\33[31m{host} | {task} => {status}\33[0m\n        \33[31m{msg}\33[0m'.format(
#                 host=d['host'], task=d['task'], status=d['status'], msg=d['result']['msg']
#             )
#             continue
#         elif d['result']['changed'] == False and d['status'] != 'ignoring':
#             color = '34m'
#         elif d['result']['changed'] == False:
#             color = '31m'
#         elif d['result']['changed'] == True:
#             color = '33m'
#         msg += '''\33[{color}{host} | {task} => {status} \33[0m\n        \33[{color}"changed": {changed}, \33[0m\n        \33[{color}"{task}": {data} \33[0m\n'''.format(
#                 color=color, host=d['host'], task=d['task'], status=d.get('status', 'None'),data=d['result'].get('msg', ''), changed=d['result'].get('changed')
#             )
#         if d['status'] == 'skipped':
#             msg += '\33[35m......%s     [%s]\33[0m\n' % ('跳过上个任务', d['host'])
#         elif d['status'] == 'ignoring':
#             msg += '\33[36m......%s     [%s]\33[0m\n' % ('忽略任务错误', d['host'])
#     return msg


from public.viewFunc.ansibleIndex import AnsibleOpt


# class AnsibleTaskApi(View):     # 跳过csrf保护机制
#     def post(self, request, *args, **kw):
#         if not request.META.get('REMOTE_ADDR') in ['172.31.72.6', '127.0.0.1', '10.20.64.29', '172.31.33.75']:
#             return HttpResponse('访问拒绝', status=403)
#         data = json.loads(request.body) if request.body else {}
#         myfunc = data.get("function", None)
#         playbook = data.get("playbook", None)
#         var = data.get('vars')
#         extra_vars = var
#         if myfunc and not playbook:
#             f = Functions.objects.filter(funcName=myfunc)[0]
#             playbook =  f.playbook
#         groupName = data.get("groupName", None)
#         print("playbook: %s, groupName: (%s), var: %s" % (playbook, groupName, var))
#         if not groupName:
#             return JsonResponse({"msg": "参数错误, 00001"})
#         if not playbook and not myfunc:
#             return JsonResponse({"msg": "参数错误, 00002"})
#         s = AnsibleOpt.ansible_playbook(
#                 groupName=groupName,
#                 playbook=playbook,
#                 extra_vars=extra_vars,
#                 **{'label': request.META.get('REMOTE_ADDR')}
#             )
#         return JsonResponse(s)
#     def get(self, request, *args, **kw):
#         dataKey = request.GET.get('dataKey', '')
#         if dataKey:
#             ad = AnsibleTasks.objects.filter(AnsibleID=dataKey)
#             if ad.count() == 1:
#                 return HttpResponse(ansible_result_analyze_jenkins(ad[0].AnsibleResult))
#         return HttpResponse('some error', status=404)