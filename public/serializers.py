from rest_framework import serializers

from .models import *


class HostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HostsLists
        fields = ('hostname', 'ip', 'ansible_user', 'ansilbe_key')


class ProjectGroupsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProjectGroups
        fields = ('groupName', 'nickName', 'hostList')


class AnsibleTasksSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AnsibleTasks
        fields = ('AnsibleID', 'CeleryID', 'TaskUser', 'GroupName', 'playbook', 'ExtraVars', 'AnsibleResult', 'CeleryResult', 'CreateTime')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class FunctionsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Functions
        fields = ('funcName', 'nickName', 'playbook')