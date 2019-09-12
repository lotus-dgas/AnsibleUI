

from rest_framework import serializers

from public.models import *

class HostsListsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostsLists
        fields = ['url', 'hostName', 'hostAddr']


from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('url', 'id', 'username')
