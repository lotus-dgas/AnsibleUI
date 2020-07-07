from public.serializers import *
from public.models import *
from rest_framework import viewsets


class UserViewSet(viewsets.ModelViewSet):
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

class AnsibleTasksViewSet(viewsets.ModelViewSet):
    """
    允许用户查看、编辑 api 路径
    """
    queryset = AnsibleTasks.objects.all()
    serializer_class = AnsibleTasksSerializer
