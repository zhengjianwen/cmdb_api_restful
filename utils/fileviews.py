#!/usr/bin/env python
# -*- coding=utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, HttpResponse
from django.views import View
from repository.models import *
from django.db.models import Count
from cmdb.settings import BASE_DIR
import json, os, xlwt, time, shutil, xlrd
from utils.formdb import AssetForm

class AssetUploadViewSet(View):
    '''
    文件上传功能，支持xls,xlsx 格式的excel.必须使用模板提交。
    
    '''

    def get(self, request, orgid):
        '''
        API Provide download file template
        :param request: 
        :param orgid: 
        :return: 
        '''
        return render(request,'upload/upload.html')
        msg = {
            "status": 1,
            "data": '',
            "msg": ''}
        if self.verification(request) or 1:
            msg['status'] = 0
            msg['data'] = '/static/filetamplate/asset_template.xlsx'
        # msg['msg'] = 'Verification does not pass'
        return HttpResponse(json.dumps(msg))

    def post(self, request, orgid):
        msg = {"status": 0, "data": '', "msg": None}
        file_path = self.wirte_excel(request)
        if not file_path:
            msg['status'] = 1
            msg['msg'] = "这个文件不是有效格式的文件"
            return HttpResponse(json.dumps(msg))

        data = self.read_excel(file_path)

        if not data:
            msg['status'] = 1
            msg['msg'] = "The file has no content"
            return HttpResponse(json.dumps(msg))

        data['orgid'] = orgid
        msg['data'] = data
        return HttpResponse(json.dumps(data))

    def wirte_excel(self, request):
        '''
        写入excel文件
        :param request: 
        :return: file path
        '''
        import os
        from cmdb.settings import BASE_DIR

        file = request.FILES.get('file')
        if '.xls' not in file.name[-5:]:
            return False

        file_path = os.path.join(BASE_DIR, 'tmp', file.name)
        with open(file_path, 'wb') as f:
            for i in file.chunks():
                f.write(i)
        return file_path

    def read_excel(self, path):
        '''
        读取文件内容并返回数据
        :param path: 
        :return: dict content
        '''
        excel = xlrd.open_workbook(path)
        # 获取表
        table_server = excel.sheet_by_name(u'server')
        table_network = excel.sheet_by_name(u'network')
        data = {}
        # 获取行数
        data.update(self.read_data(table_server))
        data.update(self.read_data(table_network))
        os.remove(path)  # 删除缓存文件
        if not data:
            return False

        return data

    def read_data(self,table):
        nrows = table.nrows
        title = None
        data = {}
        for i in range(nrows):
            # 获取美每数据
            row_val = table.row_values(i)
            if i == 0 and 'sn' in row_val:
                title = row_val  # 讲标题赋值给系统
                continue
            tmp = {'status': False, 'data': {}}
            # 将值变成键值对的方式保存
            for index, key in enumerate(title):
                tmp['data'][key] = row_val[index]

            if self.data_review(tmp['data']):
                tmp['status'] = True
            data[tmp['data']['sn']] = tmp
        print('-->',data)
        return data

    def verification(self, request):
        '''
        认证验证
        :param request: 
        :return: 
        '''
        cookie = request.COOKIES.get('rywww')
        if cookie:
            return True

    def data_review(self, data):
        '''数据验证'''
        # obj = AssetForm(data)
        # if obj.is_valid():
        #     return True
        return False


class AssetDownViewSet(View):
    '''
    down data to excel
    '''

    def get(self, request, orgid):
        msg = {
            "status": 1,
            "data": '',
            "msg": None}
        data_list = self.getdata(request, orgid)
        file_name = self.write_data_to_excel(data_list)
        if file_name:
            msg['status'] = 0
            msg["data"] = '/static/tmp/%s' % file_name
        else:
            msg['msg'] = 'File generation failed'
        return HttpResponse(json.dumps(msg))

    def write_data_to_excel(self, data_list):
        '''
        写入文件数据，返回url路径
        :param db: Filtered data
        :return: 
        '''
        if not data_list:
            return None
        excel = xlwt.Workbook()
        sheet = excel.add_sheet('database', cell_overwrite_ok=True)

        # write data
        for x, row in enumerate(data_list):
            for y, val in enumerate(row):
                sheet.write(x, y, val)
        # save data to
        # 生成文件
        today = time.time()
        file_name = str(int(today))
        file_name = file_name + '.xls'
        excel.save(file_name)
        # 移动文件 /static/tmp/file_name.xls
        old_path = os.path.join(BASE_DIR, file_name)
        new_file_path = os.path.join(BASE_DIR, 'static', 'tmp', file_name)
        if os.path.exists(old_path):
            shutil.move(old_path, new_file_path)
            return file_name

    def getdata(self, request, orgid):
        '''
        通过获取sn 和 字段名称获取数据
        :param request: 
        :param orgid: 客户id
        :return: 数据列表
        '''
        try:
            sn_list = request.GET.getlist('sn')
            title_list = tuple(request.GET.getlist('title'))
            data_objs = Asset.objects.filter(sn__in=sn_list, orgid=orgid).values_list(*title_list)
            # title_list = ['sn', 'hostname', 'vendor', 'raid', 'idc', 'rack', 'int_ip', 'ext_ip', 'ilo_ip', 'status', 'product_name', 'tags', 'cpu', 'mem', 'disk', 'owner', 'plans', 'os', 'mac', 'create_at', 'rack_unit', 'note']
            data_objs = Asset.objects.filter(orgid=orgid).values_list(*title_list)

            data_objs = list(data_objs)
            data_objs.insert(0, title_list)
            return data_objs
        except Exception as e:
            return []


class AssetCount(View):
    def get(self, request, orgid):
        msg = {"status": 1, "data": '', "msg": None}
        condition = request.GET.get('condition')
        data_sum_group_items = Asset.objects.filter(orgid=orgid).values('%s' % condition).annotate(
            c_sum=Count('%s' % condition))

        data = []
        for item in data_sum_group_items:
            tmp = {}
            tmp['name'] = item['%s' % condition]
            tmp['sum_nub'] = item['c_sum']
            data.append(tmp)
        if not data:
            msg['status'] = 0
            msg['msg'] = 'No data has been found'
        msg['data'] = data
        return HttpResponse(json.dumps(data))
