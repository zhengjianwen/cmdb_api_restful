#!/usr/bin/env python
# -*- coding=utf-8 -*-
from django.shortcuts import get_object_or_404, get_list_or_404
from api.myresponse import processdata
from rest_framework import permissions
from rest_framework import viewsets
from repository.models import Asset, NetworkDevice, Server, AssetRecord
from api.serializers import AssetSerializer, ServerSerializer, NetworkSerializer


class AssetViewSet(viewsets.ModelViewSet):
    """
    资产管理
    """
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        orgid = self.kwargs["orgid"]
        self.queryset = Asset.objects.filter(orgid=orgid)
        assetserializer = AssetSerializer(self.queryset, many=True)

        server_queryset = Server.objects.filter(asset__orgid=orgid)
        server_serializer = ServerSerializer(server_queryset, many=True)

        net_queryset = NetworkDevice.objects.filter(asset__orgid=orgid)
        network_serializer = NetworkSerializer(net_queryset, many=True)
        print(network_serializer.data)
        return processdata({
            "status": 0,
            "data": {'asset': assetserializer.data,
                     'server': server_serializer.data ,
                     'network': network_serializer.data},
            "msg": ""
        }, request)

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        orgid = self.kwargs["orgid"]
        try:
            asset_obj = Asset.objects.filter(orgid=orgid, id=pk)
            asset = AssetSerializer(asset_obj, many=True)
            if asset_obj and asset_obj.first().device_type == 'SERVER':
                obj = Server.objects.filter(asset=asset_obj)
                asset_data = ServerSerializer(obj, many=True)
            elif asset_obj and asset_obj.first().device_type == 'NETWORK':
                obj = NetworkDevice.objects.filter(asset=asset_obj)
                asset_data = NetworkSerializer(obj, many=True)
            return processdata({
                "status": 0,
                "data": {'asset': asset.data,
                         'data':asset_data.data},
                "msg": ""
            },request)
        except Exception as e:
            return processdata({
                "status": 0,
                "data":"",
                "msg": "没有此资产"
            }, request)

    def create(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        request.data.update({'orgid': orgid})
        serializer = AssetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return processdata({
            "status": 0,
            "data": "",
            "msg": "创建资产成功"
        }, request)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = self.kwargs["pk"]
        orgid = self.kwargs["orgid"]

        instance = get_object_or_404(self.queryset, id=pk, orgid=orgid)
        serializer = self.get_serializer(instance, request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": "更新成功"
        }, request)

    def destroy(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = self.kwargs["pk"]
        orgid = self.kwargs["orgid"]
        instance = get_object_or_404(self.queryset, id=pk, orgid=orgid)
        asset_obj = Asset.objects.filter(orgid=orgid, id=pk).first()
        if asset_obj and asset_obj.device_type == 'SERVER':
            Server.objects.filter(id=pk).delete()
        elif asset_obj and asset_obj.device_type == 'NETWORK':
            NetworkDevice.objects.filter(id=pk).delete()
        self.perform_destroy(instance)
        return processdata({
            "status": 0,
            "data": "",
            "msg": "删除资产成功"
        }, request)


class ServerViewSet(viewsets.ModelViewSet):
    """
    服务器资产管理
    """
    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        orgid = self.kwargs["orgid"]
        queryset = Server.objects.filter(asset__orgid=orgid)
        server_serializer = ServerSerializer(queryset, many=True)

        return processdata({
            "status": 0,
            "data": server_serializer.data,
            "msg": ""
        }, request)

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        orgid = self.kwargs["orgid"]
        servers = Server.objects.filter(asset__orgid=orgid, id=pk)
        server_serializer = ServerSerializer(servers, many=True)

        return processdata({
            "status": 0,
            "data": server_serializer.data,
            "msg": ""
        },request)

    def create(self, request, *args, **kwargs):
        serializer = ServerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return processdata({
            "status": 0,
            "data": "",
            "msg": "创建服务器成功"
        }, request)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = self.kwargs["pk"]
        orgid = self.kwargs["orgid"]

        instance = get_object_or_404(self.queryset, id=pk, asset__orgid=orgid)
        serializer = self.get_serializer(instance, request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def destroy(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        orgid = self.kwargs["orgid"]
        queryset = Server.objects.filter(asset__orgid=orgid,id=pk)
        instance = get_object_or_404(queryset)
        self.perform_destroy(instance)
        return processdata({
            "status": 0,
            "data": "",
            "msg": "删除服务器成功"
        }, request)


class NetworkDeviceViewSet(viewsets.ModelViewSet):
    """
    网络设备管理
    """
    queryset = NetworkDevice.objects.all()
    serializer_class = NetworkSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        orgid = self.kwargs["orgid"]
        queryset = NetworkDevice.objects.filter(asset__orgid=orgid)
        network_serializer = NetworkSerializer(queryset, many=True)

        return processdata({
            "status": 0,
            "data": network_serializer.data,
            "msg": ""
        }, request)

    def retrieve(self, request, *args, **kwargs):
        try:
            pk = self.kwargs["pk"]
            orgid = self.kwargs["orgid"]
            network = NetworkDevice.objects.filter(asset__orgid=orgid, id=pk)
            network_serializer = ServerSerializer(network, many=True)

            return processdata({
                "status": 0,
                "data": network_serializer.data,
                "msg": ""
            }, request)
        except Exception as e:
            return processdata({
                "status": 0,
                "data": "",
                "msg": "条件不正确"
            }, request)

    def create(self, request, *args, **kwargs):
        serializer = NetworkSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)

            return processdata({
                "status": 0,
                "data": "",
                "msg": "创建网络设备成功"
            }, request)
        return processdata({
            "status": 0,
            "data": "",
            "msg": "创建网络设备失败，数据验证失败"
        }, request)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = self.kwargs["pk"]
        orgid = self.kwargs["orgid"]

        instance = get_object_or_404(self.queryset, id=pk, asset__orgid=orgid)
        serializer = self.get_serializer(instance, request.data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return processdata({
                "status": 0,
                "data": serializer.data,
                "msg": ""
            }, request)
        return processdata({
            "status": 0,
            "data": "",
            "msg": "更新失败，%s" % serializer.error
        }, request)

    def destroy(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        orgid = self.kwargs["orgid"]
        queryset = NetworkDevice.objects.filter(asset__orgid=orgid,id=pk)
        instance = get_object_or_404(queryset)
        self.perform_destroy(instance)
        return processdata({
            "status": 0,
            "data": "",
            "msg": "删除设备成功"
        }, request)