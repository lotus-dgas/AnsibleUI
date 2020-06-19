
__author__ = '纳兰秋水'
__describe__ = '将 inventory 和 playbooks 同步到 数据库'

import os
import sys
import json
import django
path=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,path)
os.environ['DJANGO_SETTINGS_MODULE']='AnsibleUI.settings'
django.setup()
from public.models import *

def sync_projects_to_db():  # 从inventory 文件同步到db
    with open('scripts/production') as f:
        s = f.read()
    ct = [ i for i in s.split() if i ]
    k = ""
    relation = {}
    tmp = []
    for i in ct:
        if i.startswith('['):
            if k:
                relation[k] = tmp
                tmp = []
            k = i[1:-1]
        else:
            tmp.append(i)
    relation[k] = tmp
    for a,b in relation.items():
        if a == 'all': continue
        ps = ProjectGroups.objects.get_or_create(groupName=a)
        p = ps[0]
        if ps[1]:
            print('新Group：%s' % a)
        p.hostList.clear()
        for h in b:
            ts = HostsLists.objects.get_or_create(ip=h)
            t = ts[0]
            if ts[1]:
                print('新Host：%s' % h)
            p.hostList.add(t)

def sync_functions_to_db():
    ps = os.listdir('playbooks/')
    for p in ps:
        if os.path.isfile('playbooks/%s' % p):
            with open('playbooks/%s' % p) as f:
                s = f.read()
            sl = s.strip().splitlines()
            if not sl: continue
            t = sl[0]
            if not t.startswith('#') or t[1:].strip().startswith('- hosts'):
                continue
            fs = Functions.objects.get_or_create(playbook=p)
            if fs[1]:
                fs[0].nickName=t[1:].strip()
                fs[0].save()
                print("新PlayBook： %s" % p)

if __name__ == '__main__':
    sync_projects_to_db()
    sync_functions_to_db()


