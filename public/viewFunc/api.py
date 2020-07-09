from myCelery import ansible_playbook_api_29
from rest_framework.response import Response
from rest_framework import status
from public.serializers import *
from public.models import *
from rest_framework import viewsets
import random
import datetime
import string
from rest_framework import permissions


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    此视图自动提供`list`和`detail`只读操作。
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class HostViewSet(viewsets.ModelViewSet):
    """
    此视图自动提供`list`，`create`，`retrieve`，`update`和`destroy`操作。
    """
    queryset = HostsLists.objects.all()
    serializer_class = HostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ProjectViewSet(viewsets.ModelViewSet):
    """
    允许用户查看、编辑 api 路径
    """
    queryset = ProjectGroups.objects.all()
    serializer_class = ProjectGroupsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class FunctionsViewSet(viewsets.ModelViewSet):
    """
    允许用户查看、编辑 api 路径
    """
    queryset = Functions.objects.all()
    serializer_class = FunctionsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# class AnsibleTasksViewSet(viewsets.ReadOnlyModelViewSet):
class AnsibleTasksViewSet(viewsets.ModelViewSet):
    """
    允许用户查看、编辑 api 路径，以及一个额外操作的 create 方法
    """
    queryset = AnsibleTasks.objects.all()
    serializer_class = AnsibleTasksSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request, *k, **kw):
        """添加新的 `ansible task` 需要额外操作"""
        data = request.data.copy()
        groupName = request.GET.get("groupName", None)
        playbook = request.data.get('playbook')
        extra_vars = request.data.get('extra_vars', {})
        if not extra_vars.get('groupName'):
            extra_vars['groupName'] = groupName
        tid = "AnsibleApiPlaybook-drf-%s-%s" % (''.join(random.sample(string.ascii_letters + string.digits, 8)),
                                                datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        celeryTask = ansible_playbook_api_29.apply_async((tid, playbook, extra_vars))
        data.update({'AnsibleID': tid, 'CeleryID': celeryTask.task_id, 'Label': request.META.get('REMOTE_ADDR')})
        # create 只能接受 request 作为参赛，只能复写相关代码
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
