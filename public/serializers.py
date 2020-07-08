from rest_framework import serializers

from .models import *


class HostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HostsLists
        fields = ('url', 'id', 'hostname', 'ip', 'ansible_user', 'ansilbe_key')


class ProjectGroupsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProjectGroups
        fields = ('url', 'id', 'groupName', 'nickName', 'hostList')


class AnsibleTasksSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AnsibleTasks
        fields = ('url', 'id', 'AnsibleID', 'CeleryID', 'TaskUser', 'GroupName', 'playbook', 'ExtraVars',
                  'AnsibleResult', 'CeleryResult', 'Label', 'CreateTime')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'email')


class FunctionsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Functions
        fields = ('url', 'id', 'funcName', 'nickName', 'playbook')