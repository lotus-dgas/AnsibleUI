
from django.contrib import auth
from django.shortcuts import render
from django.shortcuts import redirect

def myLogin(request):
    errors = []
    data = ''
    next = request.GET.get('next') or request.GET.get('redirect_to') or '/'
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        if not request.POST.get('username',''):
            errors.append('Enter a user')
        if not request.POST.get('password',''):
            errors.append('Enter a passwd')
        if not errors:
            user = auth.authenticate(username=username,password=password)
            if user is not None and user.is_active:
                auth.login(request,user)
                return redirect('%s' % next)
            else:
                data = '登陆失败，请核对信息'
        print(errors)
    return render(request, 'login2.html', {'errors': errors, 'data': data},)

def myLogout(request):
    next = request.GET.get('next','/')
    auth.logout(request)
    return redirect('%s' % next)

from django.http import HttpResponse
def myApply(request):
    return HttpResponse('<h2 style="text-align: center;">无法申请<a href="/">反回</a></h2>')


import os
from django.core.cache import cache
from tools.config import note_base_dirt
def notes(request, *k, **kw):
    dataKey = request.GET.get('dataKey')
    data = cache.get("note_%s" % dataKey)
    if not data:
        if dataKey:
            fl = '%s/%s' % (note_base_dirt, dataKey)
            if os.path.isfile(fl):
                with open(fl)as f:
                    s = f.read()
            else: s = "错误❎"
            files = []
        else:
            files = os.listdir(note_base_dirt)
            s = ""
        data = {"msg": s, "files": files}
        cache.set("note_%s" % dataKey, data)
    else: print("Cache: %s" % dataKey)
    return render(request, "notes.html", data)
