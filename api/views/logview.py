#!/usr/bin/env python
# -*- coding=utf-8 -*-
from repository.models import *
from utils.functools import ctime


def assetrecordcreat(olddata, *args, **kwargs):
    orgid = kwargs.get('orgid')
    asset = kwargs.get('asset')
    for data in olddata:
        content = ''
        ret = AssetRecord.objects.create(content=content, orgid=orgid, asset_id=asset)
    if ret:
        return True
    return False


def errorcreat(title, content, *args, **kwargs):
    orgid = kwargs.get('orgid')
    asset = kwargs.get('asset')
    ret = ErrorLog.objects.create(orgid=orgid, asset_id=asset, title=title, content=content)
    if ret:
        return True
    return False


def cmdbinfo(orgid, title, content, *args, **kwargs):
    data = {'orgid': orgid,
            'level': 'INFO',
            'title': title,
            'content': content,
            'create_at': ctime('time')}
    ret = CmdbLog.objects.create(**data)
    return ret


def cmdbupdata(orgid, name, olddata, newdata, *args, **kwargs):
    for key in olddata:
        tmp = newdata.get(key)
        if olddata[key] != tmp:
            data = {'orgid': orgid,
                    'level': 'WARN',
                    'title': '%s更新记录' % name,
                    'content': '%s的由[%s]更新为[%s]' % (name, olddata[key], tmp),
                    'create_at': ctime('time')}
            CmdbLog.objects.create(**data)
