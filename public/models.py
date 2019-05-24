from django.db import models

class Functions(models.Model):
    funcName     = models.CharField(max_length=80,null=True,blank=True)
    nickName     = models.CharField(max_length=80,null=True,blank=True)
    playbook     = models.CharField(max_length=80,null=True,blank=False)
    def __str__(self):
        return self.funcName

class HostsLists(models.Model):
    hostName    = models.CharField(max_length=80,unique=True, null=True,blank=True)
    hostAddr    = models.CharField(max_length=80,unique=True, null=True,blank=False)
    def __str__(self):
        return self.hostAddr

class ProjectGroups(models.Model):
    groupName    = models.CharField(max_length=80,unique=True, null=True,blank=True)
    nickName     = models.CharField(max_length=80,unique=True, null=True,blank=True)
    remark       = models.TextField(blank=True)
    hostList     = models.ManyToManyField(HostsLists)
    possessFuncs = models.ManyToManyField(Functions)
    def __str__(self):
        return self.groupName

class AnsibleTasks(models.Model):
    AnsibleID  = models.CharField(max_length=80,unique=True, null=True,blank=True)
    CeleryID = models.CharField(max_length=80,unique=True, null=True,blank=True)
    # taskUser =  models.ForeignKey(WeiChatUserList, on_delete=models.CASCADE)
    # taskUser = models.CharField(
    #     max_length = 100,
    #     choices = WeiChatUserList,
    #     null = True, blank=True,
    # )
    GroupName = models.CharField(max_length=80, null=True,blank=True)
    playbook = models.CharField(max_length=80, null=True,blank=True)
    AnsibleResult = models.TextField(blank=True)
    CeleryResult  = models.TextField(blank=True)
    def __str__(self):
        return self.AnsibleID
