from django.contrib import admin

from public.models import *

admin.site.site_header = "Ansible UI"
admin.site.site_title = "运维平台"

from tools.config import inventory

# 修改 hosts 与 groups 后修改 inventory 文件
def update_inventory(change=True):
    if True:
        data = "# 请勿手动修改该文件\n"
        gs = ProjectGroups.objects.all()
        for g in gs:
            data += '\n# %s\n[%s]\n' % (g.nickName, g.groupName)
            data += '\n'.join([ i[0] for i in g.hostList.values_list('ip') ])
        with open(inventory, 'w') as f:
            f.write(data+ '\n')
        print('修改 inventory')

@admin.register(Functions)
class FunctionsAdmin(admin.ModelAdmin):
    list_display = ['playbook', 'funcName', 'nickName', ]

@admin.register(HostsLists)
class HostsListsAdmin(admin.ModelAdmin):
    list_display = ['hostname', 'ip', 'ansible_user', 'ansible_pass', 'ansilbe_key']

def hostList(obj):
    s = list(obj.hostList.values_list("ip"))
    if s:
        return ','.join([ i[0] for i in s])
    else:
        return ''

@admin.register(ProjectGroups)
class ProjectGroupsAdmin(admin.ModelAdmin):
    list_display = ['groupName', 'nickName', hostList, 'remark' ]
    filter_horizontal = ('hostList', 'possessFuncs')
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        update_inventory(change)

def AnsibleResult(obj):
    return obj.AnsibleResult[:200]

@admin.register(AnsibleTasks)
class AnsibleTasksAdmin(admin.ModelAdmin):
    list_display = ['AnsibleID', 'CeleryID', 'TaskUser',
        'GroupName', 'playbook', 'ExtraVars', AnsibleResult, 'CeleryResult', 'Label', 'CreateTime']


@admin.register(ExtraVars)
class ExtraVarsAdmin(admin.ModelAdmin):
    list_display = ['Name', 'Content', 'Remark']
