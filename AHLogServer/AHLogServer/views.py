#!/usr/bin/python
# -*- coding: <# -*- coding:UTF-8> -*-

from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
import requests

import time



logServer = ''

def hello(request):
    return  HttpResponse("Hello world! This is my first trial")

def currentTime(request):
    return  HttpResponse("Current time is : " + time.strftime('%Y-%m-%d %H:%M:%S'))

def baidu(request):
    res = requests.get('http://www.baidu.com/')
    response = res.text
    print response
    # return HttpResponse(response)
    return HttpResponse(response)

def log(request):
    # return render_to_response('index.html')
    return render(request, 'index.html', {'script': '<script>alert("账号不存在")</script>'})
    # return  HttpResponse("Hello world! This is my first trial")

def search(request):
    global logServer
    quary = request.GET.get('q')
    if len(quary):
        logServer = quary

    logFile = logServer+'/AHLogServer.txt'
    res = requests.get(logFile)
    response = res.text
    print response
    return render(request, 'log.html',{'log': response})

def clean(request):
    global logServer
    cleanCommond = logServer + '/clean'
    if len(logServer) > 0 :
        res = requests.get(cleanCommond)

    return HttpResponseRedirect('/search/?q='+logServer)
    # return render(request, 'log.html', {'log': ''})