#!/usr/bin/env python
# -*- coding=utf-8 -*-
# Time: 2017/6/27 PM4:20
# Filename: test.py
# blog:www.hairuinet.com
# Version: 1.0
__author__ = "HaiRui"
import re

mac = 'ac:bc:32:d3:d7:95'
ip = '192.168.266.1'
a = re.findall(r'^(?:\d\.|\d\d\.|1\d{2}\.|2[0-4]{1}\d\.|25[0-5]{1}\.){3}(?:\d|\d\d|1\d{2}|2[0-4]{1}\d|25[0-5]{1})',ip)
print(a)