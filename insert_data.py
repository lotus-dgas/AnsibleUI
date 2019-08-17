

import os
import sys
import django
path=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,path)
#os.environ['DJANGO_SETTINGS_MODULE']='ansible_ui.settings'
os.environ['DJANGO_SETTINGS_MODULE']='ansible_ui.settings'
django.setup()

from public.models import *
from django.contrib.auth.models import User
from tools.config import inventory


u,b = User.objects.get_or_create(username='root') 
if b:
    u.username = 'root'
    u.is_staff = True
    u.is_superuser = True
    u.set_password('1234567')
    u.save()
    print("\33[34m创建管理员，root: 12334567")
else:
    print('超级管理员已存在')


pb,b = Functions.objects.get_or_create(playbook='test_debug.yml')
if b:
    print('创建测试 playbook')
    pb.nickName = '测试Debug'
    pb.playbook = 'test_debug.yml'
    pb.save()
else:
    print('测试 playbook 已存在')


h,b = HostsLists.objects.get_or_create(hostName='localhost', hostAddr='127.0.0.1')
if b:
    print('添加本机')


g,b = ProjectGroups.objects.get_or_create(groupName='test',nickName='测试')
if b:
    print('添加测试组')


data = "# 请勿手动修改该文件\n"
gs = ProjectGroups.objects.all()
for g in gs: 
    data += '\n# %s\n[%s]\n' % (g.nickName, g.groupName)
    data += '\n'.join([ i[0] for i in g.hostList.values_list('hostAddr') ])
with open(inventory, 'w') as f:
    f.write(data+ '\n')
