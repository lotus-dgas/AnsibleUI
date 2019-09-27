
from django.shortcuts import render

def jenkins_api(request):
    return render(request, 'jenkins.html', {})

def zabbix_api(request):
    return render(request, 'zabbix.html', {})