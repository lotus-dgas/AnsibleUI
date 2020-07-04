
from django.views.generic.base import RedirectView
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

import logging
logger = logging.getLogger('ansible.ui')

class RecordRequest(MiddlewareMixin):
    # 记录访问 IP
    def process_request(self, request):
        ra = request.META.get('REMOTE_ADDR', 'None')
        if ra not in ['111.203.151.252', '118.207.127.175']:
            logger.info("%s:%s:%s:%s" % 
                (request.META.get('REMOTE_ADDR', 'None'),
                request.META.get('REMOTE_HOST', 'None'),
                request.META.get('HTTP_HOST', 'None'),
                request.get_full_path()
            ) )        
            logger.info('%s - %s - %s - %s' % (request.user, request.path ,request.GET.dict(), request.POST.dict()))
        if 'ansibleui.cn' not in request.META.get('HTTP_HOST', 'None').lower():
            #return RedirectView.as_view(url='http://ansibleui.cn')
            return redirect('http://ansibleui.cn:10089')
            
