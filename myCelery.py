#!/usr/bin/env python
#coding: utf8

"""Celery 异步操作Ansible 服务端"""

import os, sys
if os.environ.get("PYTHONOPTIMIZE", ""):
    print("开始启动")
else:
    print("\33[31m环境变量问题，Celery Client启动后无法正常执行Ansible任务，\n请设置export PYTHONOPTIMIZE=1；\n\33[32mDjango环境请忽略\33[0m")

import json
import time
from celery import Celery
from ansibleApi import *
from tools.config import BACKEND, BROKER, REDIS_ADDR, REDIS_PORT, REDIS_PD, ansible_result_redis_db, inventory, result_db
from tools.AnsibleApi_v29 import *
from celery.app.task import Task
from celery.utils.log import get_task_logger
from celery.result import AsyncResult
try:
    from rich import print
except:
    pass

import django
path=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,path)
os.environ['DJANGO_SETTINGS_MODULE']='ansible_ui.settings'
django.setup()
from public.models import *


celery_logger = get_task_logger(__name__)

appCelery = Celery("tasks", broker=BROKER, backend=BACKEND,)
appCelery.conf.task_send_sent_event = True
appCelery.conf.worker_send_task_events = True

redbeat_redis_url = "redis://localhost:6379/1"


sources = inventory


class MyTask(Task):  #毁掉
    abstract = True

    # 任务返回结果后执行
    def after_return(self, status, respose, celery_id, args, *k, **kw):
        r = redis.Redis(host=REDIS_ADDR, password=REDIS_PD, port=REDIS_PORT, db=ansible_result_redis_db)
        a = redis.Redis(host=REDIS_ADDR, password=REDIS_PD, port=REDIS_PORT, db=result_db)
        tid = args[0]
        print('MyTask: 处理 Ansible 任务结果， AnsibleID: %s, %s, %s, %s, %s, %s, %s'% (tid,  status, respose, celery_id, args, k, kw))
        rlist = r.lrange(tid, 0, -1)
        try:
            at = AnsibleTasks.objects.filter(AnsibleID=tid)[0]
            at.AnsibleResult = json.dumps([ json.loads(i.decode()) for i in rlist ])
            ct = a.get('celery-task-meta-%s' % at.CeleryID).decode()
            at.CeleryResult = ct
            at.save()
            print("同步结果至db: syncAnsibleResult !!!!!: parent_id: %s" % self.request.get('parent_id'), a, kw)
        except:
            pass
        print("%s - %s - %s - %s - %s - %s" % (status, respose, celery_id, args, k, kw))

    # 任务成功后执行
    def on_success(self, retval, task_id, args, kwargs):
        print("执行成功 notice from on_success")
        return super(MyTask, self).on_success(retval, task_id, args, kwargs)

    # 任务失败时执行
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print("执行失败 notice from on_failure")
        return super(MyTask, self).on_failure(exc, task_id, args, kwargs, einfo)


def get_inventory():
    data = []
    hs = HostsLists.objects.all()
    for h in hs:
        gs = [i.groupName for i in h.projectgroups_set.all()]
        data.append({
            'ip': h.ip,
            'username': h.ansible_user,
            'password': h.ansible_pass,
            'private_key': h.ansilbe_key,
            'groups': gs
        })
    return data


@appCelery.task(bind=True, base=MyTask)
def ansible_playbook_api_29(self, tid, playbooks, extra_vars, **kw):
    """tid 必须传入，不能生成"""
    # psources = kw.get('sources') or extra_vars.get('sources') or sources
    if isinstance(playbooks, str):
        playbooks = ['playbooks/%s' % playbooks]

    AnsiblePlaybookExecApi29(tid, playbooks, get_inventory(), extra_vars)
    return 'ok'


if __name__ == "__main__":
    appCelery.worker_main()

# celery -A myCelery worker -l info
# celery multi start 1 -A myCelery -l info -c4 --pidfile=tmp/celery_%n.pid -f logs/celery.log
# celery multi restart 1 -A myCelery -l info -c4 --pidfile=tmp/celery_%n.pid -f logs/celery.log
# celery multi stop 1 -A myCelery -l info -c4 --pidfile=tmp/celery_%n.pid
