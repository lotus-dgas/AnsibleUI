#coding: utf8
import random, urllib, json, hashlib
from django.http import Http404
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.http import HttpResponsePermanentRedirect
from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
# from tools.weiChat import *
from django.core.signing import Signer
from functools import wraps
import re

# from config import Env
regex = re.compile('^HTTP_')

def ProxyAuth(func):
    @wraps(func)
    def wrapped_func(request, *args, **kw):
        # if not request.META.get("HTTP_WEICHAT_USER"):
        #     return HttpResponseForbidden()
        #     # return HttpResponse(status=403)
        #     # return HttpResponseNotFound('<h1>Page not found</h1>')
        #     pass
        print("\33[36mURI %s\33[0m"%request.build_absolute_uri())
        # print(dict((regex.sub('', header), value) for (header, value)
        #            in request.META.items() if header.startswith('HTTP_')))
        print("\33[34mProxy: is_ajax:%s,WeiChat:[%s],AddR:[%s], Custome:[%s], X_F_F:%s, UA:%.10s\33[0m" % (
                request.is_ajax(),
                request.META.get("HTTP_WEICHAT_USER", "None"),
                request.META.get("REMOTE_ADDR", "None"),
                request.META.get("HTTP_CUSTOMPROXY", "None"),
                request.META.get("HTTP_X_FORWARDED_FOR", "None"),
                request.META.get("HTTP_USER_AGENT", "None"),
            ))
        return func(request, *args, **kw)
    return wrapped_func
