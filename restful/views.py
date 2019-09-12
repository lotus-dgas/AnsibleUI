from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import generics
from rest_framework import permissions

from restful.serializers import *

from public.models import *
from django.contrib.auth.models import User

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'hostslists': reverse('hostslists-list', request=request, format=format)
    })

class UserList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveAPIView):
    # 权限控制
    permission_classes = (permissions.IsAuthenticated, )
    queryset = User.objects.all()
    serializer_class = UserSerializer

class HostsListsList(generics.ListAPIView):
    queryset = HostsLists.objects.all()
    serializer_class = HostsListsSerializer

class HostsListsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = HostsLists.objects.all()
    serializer_class = HostsListsSerializer
