from django.shortcuts import render
from django.views import View
import json, random, datetime

class Index(View):
    def get(self, request, *k, **kw):
        data = {}
        t = datetime.date.today()
        data['x'] = json.dumps([  (t+datetime.timedelta(i)).strftime('%m/%d') for i in range(-6, 1) ])
        data['y'] = json.dumps([ random.randint(2,28) for i in  range(7) ])
        return render(request, 'base_public.html', data)