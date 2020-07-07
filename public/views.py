
import ast
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView
from django.shortcuts import redirect

from public.models import *
from public.viewFunc.ansibleIndex import AnsibleOpt


class Index(View):

    def get(self, request, *k, **kw):
        data = {}
        return render(request, 'base_adminlte.html', data)


class AnsibleTaskList(ListView):
    """Ansible Tasks 列表页"""
    model = AnsibleTasks


class AnsibleTaskDetail(DetailView):
    """Ansible Tasks 详情页"""
    model = AnsibleTasks
    context_object_name = 't'


class GroupsDetail(DetailView):
    model = ProjectGroups


class GroupsList(ListView):
    """项目组列表页"""
    model = ProjectGroups


class HostsList(ListView):
    """主机列表页"""
    model = HostsLists


class HostsDetail(DetailView):
    """主机详情页面"""
    model = HostsLists


class PlaybookList(ListView):
    """Playbook 列表页"""
    model = Functions


class PlaybookDetail(DetailView):
    """playbook 详情页"""
    model = Functions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pb = context['object'].playbook
        with open('playbooks/%s' % pb)as f:
            s = f.read()
        context['yml_content'] = '```yaml\n%s\n```' % s

        return context


class TemplateReturn(LoginRequiredMixin, View):
    """添加 ansible playbook 任务也没"""

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


class AnsibleTask(LoginRequiredMixin, View):    #ansibe Http 任务推送接口
    def get(self, request, *args, **kw):
        user = request.META.get("HTTP_WEICHAT_USER")
        user = request.user
        myfunc = request.GET.get("function", None)
        playbook = request.GET.get("playbook", None)
        var = request.GET.get('vars')
        extra_vars = ast.literal_eval(var) if var else {}
        if myfunc and not playbook:
            f = Functions.objects.filter(funcName=myfunc)[0]
            playbook =  f.playbook
        groupName = request.GET.get("groupName", None)
        if not groupName:
            return JsonResponse({"msg": "参数错误"})
        if not playbook and not myfunc:
            return JsonResponse({"msg": "参数错误"})
        s = AnsibleOpt.ansible_playbook(
                groupName=groupName,
                playbook=playbook,
                user=user,
                extra_vars=extra_vars,
                **{'label': request.META.get('REMOTE_ADDR')}
            )
        # s = extra_vars
        # return redirect('/ansible/get_Ansible_Tasks/?dataKey=%s' % s.get('tid'))
        return redirect('/ansible/task/%s/' % s.get('id'))

        # 参数： groupName, (playbook | myfunc), 不支持 茉莉花 调用
    def post(self, request, *k, **kw):
        return JsonResponse({"msg": "err"})