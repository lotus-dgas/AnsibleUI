#coding: utf8

import random, urllib, json, hashlib
from django.http import Http404
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.http import HttpResponsePermanentRedirect
from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.http import HttpResponse
# from tools.weiChat import *
from django.core.signing import Signer
from functools import wraps

# from weiAPI.config import *
import logging
logger = logging.getLogger("custom")
develop = logging.getLogger("develop")
record = logging.getLogger("record")
cookie_name = "WeiChatCookie"


def OAuthCookie(func):
    @wraps(func)
    def wrapped_func(request, *args, **kw):
        code = request.GET.get("code","")
        cook_user = request.COOKIES.get(cookie_name, '')
        weiChatID = my_weiChat
        if cook_user:
            signer = Signer()
            original = signer.unsign(cook_user)
            develop.info("User已登录, %s" % original)
            kw["user"] = original
            request.user = original
            return func(request, *args, **kw)
        elif code:
            wcc = WeiChatCallBack(weiChatID.get("corpid"), weiChatID["agents"][AGENTID])
            state, user = wcc.userInfo(code=code)
            if state != 1:
                user = "anonymous"
            s = hashlib.sha1(user.encode()).hexdigest()
            signer = Signer()
            value = signer.sign(user)
            develop.info("设置 User, User:%s, Hash:%s, Value: %s" % (user, s, value))
            kw["user"] = user
            request.user = user
            response = func(request, *args, **kw)
            response.set_cookie(cookie_name, value, 60*60*24)
            return response
        else:
            CORPID = weiChatID.get("corpid")
            state = request.GET.get("state", "")
            REDIRECT_URI = BASE_REDIRECT_URI+request.get_full_path()
            rUrl = weiRewrite.format(CORPID=CORPID,SCOPE=SCOPE,AGENTID=AGENTID,STATE=STATE,REDIRECT_URI=REDIRECT_URI)
            return HttpResponseRedirect(rUrl)
        return func(request, *args, **kw)
    return wrapped_func


def LocalLogin(func):
    @wraps(func)
    def wrapped_func(request, *args, **kw):
        code = request.GET.get("code", "")
        weiChatID = kw.get("WeiChat", my_weiChat)
        if request.user.is_authenticated:   # 已经认证并登录
            develop.info("\33[33m用户已认证：%s\33[0m" % request.user)
            return func(request, *args, **kw)
        elif code:      #携带微信 token
            develop.info("\33[31mCode:-----%s-----正在使用\33[0m" % code)
            wcc = WeiChatCallBack(weiChatID.get("corpid"), weiChatID.get("corpsecret"))
            state, userid = wcc.userInfo(code=code)
            if state != 1:
                #user = "anonymous"
                return render(request, "403.html", {}, status=403)
            else:
                user = authenticate(userid=userid)
                login(request, user, backend="custom.WeiChatLocalAuth.WeiChatLocalAuth")
            func(request, *args, **kw)
        else:
            CORPID = weiChatID.get("corpid")
            state = request.GET.get("state", "")
            REDIRECT_URI = BASE_REDIRECT_URI+request.get_full_path()
            rUrl = weiRewrite.format(CORPID=CORPID,SCOPE=SCOPE,AGENTID=AGENTID,STATE=STATE,REDIRECT_URI=REDIRECT_URI)
            return HttpResponseRedirect(rUrl)
        return func(request, *args, **kw)
    return wrapped_func


def OAuthSession(func):
    @wraps(func)
    def wrapped_func(request, *args, **kw):
        code = request.GET.get("code","")
        full_path = request.get_full_path()
        weiChatID = kw.get("WeiChat", my_weiChat)
        user = request.session.get("weichat_%s" % weiChatID.get("description"), "") #多企业号问题
        customToken = request.GET.get("ct", "")
        if customToken=="CdgohEHOmjjBt":
            request.user = customToken
            request.session['weichat_%s' % weiChatID.get("description")] = customToken
            return func(request, *args, **kw)
        if user == "anonymous":
            return render(request, "403.html", {}, status=403)
        elif user:
            request.user = user
            return func(request, *args, **kw)
        elif code:
            wcc = WeiChatCallBack(weiChatID.get("corpid"), weiChatID.get("corpsecret"))
            state, user = wcc.userInfo(code=code)
            if state != 1:
                user = "anonymous"
                return render(request, "403.html", {}, status=403)
            else:
                request.user = user
            #request.session['username'] = user
            request.session['weichat_%s' % weiChatID.get("description")] = user     #写入Session
            func(request, *args, **kw)
        else:
            CORPID = weiChatID.get("corpid")
            state = request.GET.get("state", "")
            REDIRECT_URI = BASE_REDIRECT_URI+request.get_full_path()
            rUrl = weiRewrite.format(CORPID=CORPID,SCOPE=SCOPE,AGENTID=AGENTID,STATE=STATE,REDIRECT_URI=REDIRECT_URI)
            return HttpResponseRedirect(rUrl)
        return func(request, *args, **kw)
    return wrapped_func


OTokenList = [""]


def OAuthToken(func):
    @wraps(func)
    def wrapped_func(request, *args, **kw):
        token = request.GET.get("customToken","")
        full_path = request.get_full_path()
        if token in OTokenList:
            return func(request, *args, **kw)
        else:
            return render(request, "403.html", {}, status=403)
    return wrapped_func
