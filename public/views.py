from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.http import HttpResponse, JsonResponse

import json, random, datetime

from public.models import *

class Index(View):
    def get(self, request, *k, **kw):
        data = {}
        # t = datetime.date.today()
        # tmp = [  (t+datetime.timedelta(i)) for i in range(-6, 1) ]
        # data['x'] = [  i.strftime('%m/%d') for i in tmp ]
        # data['y'] = [AnsibleTasks.objects.filter(AnsibleID__contains=i.strftime('%Y%m%d')).count() for i in tmp]
        # data['y'] = [ random.randint(2,28) for i in  range(7) ]
        # return render(request, 'base_public.html', data)
        return render(request, 'base_adminlte.html', data)


class AnsibleTaskList(ListView):
    model = AnsibleTasks


class AnsibleTaskDetail(DetailView):
    model = AnsibleTasks
    context_object_name = 't'


class GroupsDetail(DetailView):
    model = ProjectGroups


class GroupsList(ListView):
    model = ProjectGroups


class HostsList(ListView):
    model = HostsLists


class HostsDetail(DetailView):
    model = HostsLists


class PlaybookList(ListView):
    model = Functions


class PlaybookDetail(DetailView):
    model = Functions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pb = context['object'].playbook
        with open('playbooks/%s' % pb)as f:
            s = f.read()
        context['yml_content'] = '```yaml\n%s\n```' % s

        return context


class TemplateReturn(LoginRequiredMixin, View):
    login_url = '/account/login'
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kw):
        print(args, kw)
        template_file = kw.get('template_file', '')

        groups = ProjectGroups.objects.all()
        functions = Functions.objects.all()

        return render(request, template_file, {'groups': groups, 'functions': functions})

    def post(self, request, *k, **kw):
        return JsonResponse({'data': {'k': k, 'kw': kw}})
