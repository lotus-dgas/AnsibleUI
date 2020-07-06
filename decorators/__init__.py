#coding: utf8

from django.http import Http404
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import render
from functools import wraps
import json
import string
import random
from django.http import HttpResponse
from decorators.CustomAuth import OAuthSession, LocalLogin

import logging
logger = logging.getLogger("custom")
develop = logging.getLogger("develop")
record = logging.getLogger("record")


def RecordIP(func):
    @wraps(func)
    def wrapped_func(request, *args, **kw):
        REQ = ''.join(random.sample(string.ascii_letters + string.digits, 10))
        kw["REQ"] = REQ
        client = request.META.get("HTTP_USER_AGENT")
        (a,b) = (request.META.get("REMOTE_ADDR"), request.META.get("HTTP_X_FORWARDED_FOR"))
        record.info("Req:%s | Path:%s | REMOTE_ADDR:%s | HTTP_X_FORWARDED_FOR: %s | Client: %s" % (REQ, request.get_full_path(),a,b,client))
        return func(request, *args, **kw)
    return wrapped_func


PresentAuth = LocalLogin
#PresentAuth = OAuthSession
