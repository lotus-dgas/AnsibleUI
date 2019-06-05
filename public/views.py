from django.shortcuts import render
from django.views import View
import json, random, datetime


from public.models import *
class Index(View):
    def get(self, request, *k, **kw):
        data = {}
        t = datetime.date.today()
        tmp = [  (t+datetime.timedelta(i)) for i in range(-6, 1) ]
        data['x'] = [  i.strftime('%m/%d') for i in tmp ]
        data['y'] = [AnsibleTasks.objects.filter(AnsibleID__contains=i.strftime('%Y%m%d')).count() for i in tmp]
        # data['y'] = [ random.randint(2,28) for i in  range(7) ]
        return render(request, 'base_public.html', data)