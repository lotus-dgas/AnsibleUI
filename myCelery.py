#!/usr/bin/env python
#coding: utf8
"Celery 异步操作Ansible 服务端"

import os, sys
if os.environ.get("PYTHONOPTIMIZE", ""):
    print("开始启动")
else:
    print("\33[31m环境变量问题，Celery Client启动后无法正常执行Ansible任务，\n请设置export PYTHONOPTIMIZE=1；\n\33[32mDjango环境请忽略\33[0m")

import json
import time
from celery import Celery
from ansibleApi import *
from tools.config import BACKEND, BROKER, REDIS_ADDR, REDIS_PORT, REDIS_PD, ansible_result_redis_db
from celery.app.task import Task
from celery.utils.log import get_task_logger
from celery.result import AsyncResult
celery_logger = get_task_logger(__name__)

appCelery = Celery("tasks",broker=BROKER,backend=BACKEND,)
sources = "scripts/inventory"

class MyTask(Task): #毁掉
    def on_success(self, retval, task_id, args, kwargs):
        print("执行成功 notice from on_success")
        return super(MyTask, self).on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # print('Celery Task Exec Fail, reason: {0}'.format(exc))
        # print('Celery Task Exec Fail, %s - %s - %s - %s' % (task_id, args, kwargs, einfo))
        # task_id 是celery ID， args[0] 为ansibleID
        r = redis.Redis(host=REDIS_ADDR, password=REDIS_PD, port=REDIS_PORT, db=ansible_result_redis_db)
        a = redis.Redis(host=REDIS_ADDR, password=REDIS_PD, port=REDIS_PORT, db=4)
        tid = args[0]
        rlist = r.lrange(tid, 0, -1)
        try:
            at = AnsibleTasks.objects.filter(AnsibleID=tid)[0]
            at.AnsibleResult = json.dumps([ json.loads(i.decode()) for i in rlist ])
            ct = a.get('celery-task-meta-%s' % at.CeleryID).decode()
            at.CeleryResult = ct
            at.save()
            print("同步结果至db: syncAnsibleResult !!!!!: parent_id: %s" % self.request.get('parent_id'), a, kw)
        except: pass
        return super(MyTask, self).on_failure(exc, task_id, args, kwargs, einfo)

@appCelery.task
def ansibleExec(tid, groupname, tasks=[]):
    vars = {"project": "Lotus"} #额外参数
    AnsibleApi(tid, groupname, tasks, sources, vars)
    return None

@appCelery.task
def ansiblePlayBook(tid, pb=["playbooks/t.yml"]):
    AnsiblePlaybookApi(tid, pb, sources)
    return None

@appCelery.task(bind=True,base=MyTask)  # 
def ansiblePlayBook_v2(self,tid, pb, extra_vars, **kw):
    psources = kw.get('sources') or extra_vars.get('sources') or sources
    print("PlayBook File: %s，groupName: %s, psources: %s, Vars: %s" % (pb, extra_vars.get("groupName", "None"), psources, extra_vars))
    AnsiblePlaybookApi_v2(tid, ["playbooks/%s"%pb], psources, extra_vars)
    return 'success!!'

import os
import sys
import django
path=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,path)
if sys.version.startswith('3.7'):
    os.environ['DJANGO_SETTINGS_MODULE']='AnsibleUI.settings'
else:
    os.environ['DJANGO_SETTINGS_MODULE']='ansibleUI.settings'
django.setup()
from public.models import *

@appCelery.task(bind=True)
def syncAnsibleResult(self, ret, *a, **kw):     # 执行结束，结果保持至db
    # celery_logger.info(self.request.__dict__)
    c = AsyncResult(self.request.get('parent_id'))
    celery_logger.info(c.result)
    tid = kw.get('tid', None)
    if tid:
        r = redis.Redis(host=REDIS_ADDR, password=REDIS_PD, port=REDIS_PORT, db=ansible_result_redis_db)
        a = redis.Redis(host=REDIS_ADDR, password=REDIS_PD, port=REDIS_PORT, db=4)
        rlist = r.lrange(tid, 0, -1)
        if rlist:
            at = AnsibleTasks.objects.filter(AnsibleID=tid)[0]
            at.AnsibleResult = json.dumps([ json.loads(i.decode()) for i in rlist ])
            ct = a.get('celery-task-meta-%s' % at.CeleryID).decode()
            at.CeleryResult = ct
            at.save()
            print("同步结果至db: syncAnsibleResult !!!!!: parent_id: %s" % self.request.get('parent_id'), a, kw)
    else: pass

############  TEST  ###########
@appCelery.task(bind=True,base=MyTask)
def myTest(self, g, *a, **kw):     #bind 将获取自身信息
    celery_logger.info(self.request.__dict__)
    print("myTest: %s, %s, %s" % (g, a, kw))
    return g

@appCelery.task()
def myLink(key, *a, **kw):
    print("%s, %s, %s" % (key, a, kw))
    return "%s: %s" % (key, "Link")

# def on_result_ready(result):
#     # myTask.delay("a").then(on_result_ready)
#     print('~~~~~~~~~~Received result for id %r: %r' % (result.id, result.result,))

if __name__ == "__main__":
    appCelery.worker_main()

# celery -A myCelery worker -l info
# celery multi start 1 -A myCelery -l info -c4 --pidfile=tmp/celery_%n.pid -f logs/celery.log
# celery multi start 3 -A myCelery -l info -c4 --pidfile=tmp/celery_%n.pid -f logs/celery.log
# celery multi restart 1 -A myCelery -l info -c4 --pidfile=tmp/celery_%n.pid -f logs/celery.log
# celery multi stop 1 -A myCelery -l info -c4 --pidfile=logs/celery_%n.pid
