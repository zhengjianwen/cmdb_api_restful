#!/usr/bin/env python
# -*- coding=utf-8 -*-
# Time: 2017/6/29 AM11:15
# Filename: functools.py
# blog:www.hairuinet.com
# Version: 1.0
__author__ = "HaiRui"
import re, time


def ipverification(data):
    '''
    验证ip地址格式的函数
    :param data: 
    :return: 
    '''
    if len(data) < 7 or len(data) > 15:
        return False
    ret = re.match(r'(?:\d\.|\d\d\.|1\d{2}\.|2[0-4]{1}\d\.|25[0-5]{1}\.){3}(?:\d|\d\d|1\d{2}|2[0-4]{1}\d|25[0-4])', data)
    if not ret:
        return False
    return ret.group()


def macverification(data):
    '''
    验证mac地址的函数，只匹配ipv4的
    :param data: 
    :return: 
    '''
    ret = re.match(r'^(?:[0-9a-fA-F]{2}:){5}(?:[0-9a-fA-F]{2}){1}', data)
    if ret:
        return ret.group()
    return False


def ctime(dtype='data'):
    if dtype == 'data':
        return time.strftime("%F", time.gmtime())
    elif dtype == 'time':
        return time.strftime("%F %T", time.gmtime())


def mask(nub_bit):
    netmask = ''

    return netmask
