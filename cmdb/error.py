#!/usr/bin/env python
# -*- coding=utf-8 -*-
# Time: 2017/6/27 PM12:03
# Filename: error.py
# blog:www.hairuinet.com
# Version: 1.0
__author__ = "HaiRui"
from django.shortcuts import HttpResponse

def error(request):
    return HttpResponse('404')