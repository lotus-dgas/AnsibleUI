from myCelery import ansible_playbook_api_29
from rest_framework.response import Response
from rest_framework import status
from public.serializers import *
from public.models import *
from rest_framework import viewsets
import random
import datetime
import string


class UserViewSet(viewsets.ModelViewSet):
    """
    用户修改的 List，Detail
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class HostViewSet(viewsets.ModelViewSet):
    """
    允许用户查看、编辑 api 路径
    """
    queryset = HostsLists.objects.all()
    serializer_class = HostSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """
    允许用户查看、编辑 api 路径
    """
    queryset = ProjectGroups.objects.all()
    serializer_class = ProjectGroupsSerializer


class FunctionsViewSet(viewsets.ModelViewSet):
    """
    允许用户查看、编辑 api 路径
    """
    queryset = Functions.objects.all()
    serializer_class = FunctionsSerializer


class AnsibleTasksViewSet(viewsets.ReadOnlyModelViewSet):
    """
    允许用户查看、编辑 api 路径，以及一个额外操作的 create 方法
    """
    queryset = AnsibleTasks.objects.all()
    serializer_class = AnsibleTasksSerializer


