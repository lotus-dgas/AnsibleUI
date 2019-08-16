

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


