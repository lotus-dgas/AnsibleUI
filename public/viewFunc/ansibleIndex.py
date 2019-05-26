#coding: utf8
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views import View
import json, datetime, redis
from myCelery import ansiblePlayBook_v2, ansibleExec, syncAnsibleResult
from public.models import *
from decorators.Proxy import ProxyAuth
import logging
logger = logging.getLogger('ansible.ui')
class AnsibleOpt:       #ansible 执行 jiekou , 传如香港参赛
    @staticmethod
    def ansible_playbook(groupName, playbook, user=None, extra_vars={}):
        tid = "AnsibleApiPlaybook-%s" % datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        extra_vars["groupName"] = groupName
        # celeryTask = ansiblePlayBook_v2.delay(tid, playbook, extra_vars)
        logger.info("添加Ansilb-Playbook执行；%s" % playbook)
        celeryTask = ansiblePlayBook_v2.apply_async((tid, playbook, extra_vars), link=syncAnsibleResult.s(tid=tid)) # ansible结果保持
        # celeryTask = ansiblePlayBook_v2.apply_async((tid, playbook, extra_vars))
        AnsibleTasks(AnsibleID=tid,
                CeleryID=celeryTask.task_id,
                # taskUser=user,
                GroupName=groupName,
                playbook=playbook).save()
        return {"playbook": playbook, "extra_vars": extra_vars, "tid": tid, "celeryTask": celeryTask.task_id, "groupName": groupName}
    @staticmethod
    def ansible_opt():
        tid = "AnsibleApiOpt-%s" % datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        tasks = []
        celeryTask = ansibleExec.delay(tid, groupName, tasks)
        return {'tid': tid, 'celeryTask': celeryTask.task_id, "groupName": groupName}
    
    @staticmethod
    def push_task():
        return {}

class AnsibleData:  #Ansible 数据接口
    def __init__(self, request=None, *args, **kw):
        self.request = request
        self.is_ajax = request.is_ajax()
        self.rType = request.GET.get("rType") or kw.get("rType") or "html"
        self.ua = "phone" if ( "iPhone" in request.META.get("HTTP_USER_AGENT") or "Android" in  request.META.get("HTTP_USER_AGENT")) else ""
        self.args = args
        self.kw = kw
        self.dataKey = kw.get("dataKey") or request.GET.get("dataKey") or ""
        self.ret = ret = {"args": args, "kw": kw, "get": request.GET}
        print("\33[46mrType: %s, ua: %s, args: %s, kw: %s, dataKey: %s\33[0m" % (self.rType, self.ua, self.args, self.kw, self.dataKey))
    def dashboard(self, *args, **kw):
        return render(self.request, "ansible/dashboard.html", {})
    def get_hosts(self, *args, **kw):
        hosts = HostsLists.objects.all()
        return render(self.request, "ansible/lookup.html", {'hosts': hosts})
    def get_groups(self, *args, **Kw):
        groups = ProjectGroups.objects.all()
        return render(self.request, "ansible/lookup.html", {'groups': groups})
    def get_funcs(self, *args, **kw):
        funcs = Functions.objects.all()
        return render(self.request, "ansible/lookup.html", {'funcs': funcs})
    def get_Ansible_Tasks(self, *args, **kw):   # 获取任务
        print("dataKey: %s" % args)
        if args[0]:
            at = AnsibleTasks.objects.filter(AnsibleID=args[0])
            return render(self.request, "ansible/result.html", {'t': at[0]})
        else:
            at = AnsibleTasks.objects.values()
        if self.rType in ["html"]:
            return render(self.request, "ansible/tasks.html", {'AnsibleTasks': at})
        return list(at)
    def get_Ansible_Results(self, *args, **kw):     #获取结果
        if self.rType in ["html"] :
            return render(self.request, "ansible/tasks.html", {})
        r = redis.Redis(host=Env.ansible_result_redis_host, port=Env.ansible_result_redis_port, db=10)
        if self.dataKey:
            ret = r.lrange(self.dataKey, 0, -1)
        else:
            ret = []
        return [ json.loads(i.decode()) for i in ret ]
    def get_Celery_Result(self, dataKey, *args, **kw):  # 获取Celery 结果
        r = redis.Redis(host=Env.ansible_result_redis_host, port=Env.ansible_result_redis_port, db=4)
        dataKey = kw.get("dataKey") or args[0] or ""
        if dataKey:
            ret = r.get("celery-task-meta-%s" % dataKey)
        else:
            ret = b'{}'
        return json.loads(ret.decode())
    def push_task(self, dataKey, *args, **kw):  #
        return render(self.request, 'ansible/push.html', {})
    def push_playbook(self, dataKey, *args, **kw):  #
        groups = ProjectGroups.objects.all()
        functions = Functions.objects.all()
        return render(self.request, 'ansible/playbook_index.html', {'groups': groups, 'functions': functions})

class AnsibleTask(View):    #ansibe Http 任务推送接口
    def get(self, request, *args, **kw):
        # print()
        user = request.META.get("HTTP_WEICHAT_USER")
        myfunc = request.GET.get("function", None)
        playbook = request.GET.get("playbook", None)
        extra_vars = dict(request.GET)
        if myfunc and not playbook:
            f = Functions.objects.filter(funcName=myfunc)[0]
            playbook =  f.playbook
        groupName = request.GET.get("groupName", None)
        if not groupName:
            return JsonResponse({"msg": "参数错误"})
        if not playbook and not myfunc:
            return JsonResponse({"msg": "参数错误"})
        print("playbook: %s, groupName: %s" % (playbook, groupName))
        print(json.dumps(dict(request.GET), indent=4))
        s = AnsibleOpt.ansible_playbook(groupName=groupName, playbook=playbook, user=user, extra_vars=extra_vars)
        # s = extra_vars
        return redirect('/ansible/get_Ansible_Tasks/?dataKey=%s' % s.get('tid'))
        # 参数： groupName, (playbook | myfunc), 不支持 茉莉花 调用
    def post(self, request, *k, **kw):
        return JsonResponse({"msg": "err"})

@ProxyAuth
def tasks(request, *gs, **kw):
    return render(request, "ansible/index.html", {})

class AnsibleRequestApi(View):
    def get(self, request, *k, **kw):
        dataName = kw.get("dataName", "")
        dataKey = kw.get("dataKey") or request.GET.get("dataKey") or ""
        ad = AnsibleData(request, *k, **kw)
        if hasattr(ad, dataName):
            if callable(ad.__getattribute__(dataName)):
                data = ad.__getattribute__(dataName)(dataKey, **kw)   #V3;
                if type(data) is HttpResponse:
                    return data
            else:
                data = ad.__getattribute__(dataName)
                print("AD 属性：%s, 内容: %s" % (dataName, data))
        else:
            data = {"msg": "非有效操作"}
            # return HttpResponse(json.dumps(data, ensure_ascii=False),status=403)
            return render(request, 'ansible/error.html', data, status=403)
        ret = {"args": args, "kw": kw, "get": request.GET ,"data": data}
        return JsonResponse({'data': {'k': k, 'kw':kw}})

    def post(self, request, *k, **kw):
        return JsonResponse({'data': {'k': k, 'kw': kw}})
# class AnsibleAjax(View):    #Ajax 访问接口
#     def get(self, request, *args, **kw):
#         print(request.META.get("HTTP_X_REQUESTED_WITH", "非Ajax请求"))
#         print("Request: %s \nArgs: %s\nKW: %s" % (request.GET.dict(), args, kw))
#         dataName = kw.get("dataName", "")
#         dataKey = kw.get("dataKey") or request.GET.get("dataKey") or ""
#         ad = AnsibleData(request, *args, **kw)
#         if hasattr(ad, dataName):
#             if callable(ad.__getattribute__(dataName)):
#                 data = ad.__getattribute__(dataName)(dataKey, **kw)   #V3;
#                 if type(data) is HttpResponse:
#                     return data
#             else:
#                 data = ad.__getattribute__(dataName)
#                 print("AD 属性：%s, 内容: %s" % (dataName, data))
#         else:
#             data = {"msg": "非有效操作"}
#             return HttpResponse(json.dumps(data, ensure_ascii=False),status=403)
#         ret = {"args": args, "kw": kw, "get": request.GET ,"data": data}
#         return JsonResponse(ret)

#     def post(self, request, *args, **kw):
#         playbook = request.POST.get("playbook", None)
#         groupName = request.POST.get("groupName", None)
#         if not playbook or not groupName:
#             return JsonResponse({"erro": "参数错误"})
#         extra_vars = {}
#         s = AnsibleOpt.ansible_playbook(groupName=groupName, playbook=playbook, user=request.META.get("HTTP_WEICHAT_USER"), extra_vars=extra_vars)
#         return JsonResponse(s)



