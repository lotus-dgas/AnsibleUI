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

class inv:
    def __init__(self, gn, nn, hosts=[]):
        print('\33[31minit: %s\33[0m' % gn)
        self.gn = gn
        self.nn = nn
        self.hosts = hosts

hs = HostsLists.objects.prefetch_related('ProjectGroups').values('projectgroups__nickName', 'projectgroups__groupName', 'ip')
d = {}
for h in hs:
    gn = h.get('projectgroups__groupName')
    nn = h.get('projectgroups__nickName')
    hc = h.get('ip')
    if gn is None:
        gn = 'extraGroup'
        nn = '额外主机'
    a = d.get(gn) or  inv(gn, nn, [])
    a.hosts.append(hc)
    d[gn] = a

f = open('scripts/newinventory', 'w')
for i,j in d.items():
    print('%s : %s - %s - %s' % (i, j.gn, j.nn, j.hosts))
    f.write('[%s]\n# %s\n%s\n\n' % (i, j.nn, '\n'.join(j.hosts)))
f.close()