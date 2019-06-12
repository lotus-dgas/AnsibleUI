from django.contrib import admin

from public.models import *

admin.site.site_header = "Ansible UI"
admin.site.site_title = "运维平台"

@admin.register(Functions)
class FunctionsAdmin(admin.ModelAdmin):
    list_display = ['playbook', 'funcName', 'nickName', ]

@admin.register(HostsLists)
class HostsListsAdmin(admin.ModelAdmin):
    list_display = ['hostName', 'hostAddr']

def hostList(obj):
    s = list(obj.hostList.values_list("hostAddr"))
    if s:
        return ','.join([ i[0] for i in s])
    else:
        return ''

@admin.register(ProjectGroups)
class ProjectGroupsAdmin(admin.ModelAdmin):
    list_display = ['groupName', 'nickName', hostList, 'remark' ]
    filter_horizontal = ('hostList', 'possessFuncs')

def AnsibleResult(obj):
    return obj.AnsibleResult[:200]

@admin.register(AnsibleTasks)
class AnsibleTasksAdmin(admin.ModelAdmin):
    list_display = ['AnsibleID', 'CeleryID', 'TaskUser',
        'GroupName', 'playbook', 'ExtraVars', AnsibleResult, 'CeleryResult', 'Label', 'CreateTime']
