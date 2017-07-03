from django.shortcuts import get_object_or_404, get_list_or_404
from repository.models import *
from rest_framework import status
from rest_framework.decorators import api_view
from api.views.logview import assetrecordcreat, errorcreat
from cmdb.settings import CONTENT_TYPE
from rest_framework import generics, viewsets
from api.myresponse import processdata
from rest_framework import permissions
from api.serializers import *
from api.views.logview import cmdbinfo, cmdbupdata


class LiaisonViewSet(viewsets.ModelViewSet):
    """
    API 处理联系人信息
    """
    queryset = Liasion.objects.all()
    serializer_class = LiaisonSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        self.queryset = Liasion.objects.filter(orgid=orgid)
        serializer = LiaisonSerializer(self.queryset, many=True)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def retrieve(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        pk = self.kwargs['pk']  # Vendor
        liaison = get_object_or_404(self.queryset, vendor_id=pk, orgid=orgid)
        serializer = LiaisonSerializer(liaison)

        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def create(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        request.data.update({'orgid': orgid})
        if Liasion.objects.filter(name=request.data['name'], orgid=orgid).count() == 0:
            serializer = LiaisonSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return processdata({
                "status": 0,
                "data": "",
                "msg": "创建联系人成功"
            }, request)
        return processdata({
            "status": 1,
            "data": "",
            "msg": "vendor liaison existed"
        }, request)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        orgid = self.kwargs['orgid']
        pk = self.kwargs['pk']
        instance = get_object_or_404(self.queryset, name=pk, orgid=orgid)
        serializer = self.get_serializer(instance, request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def destroy(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        orgid = self.kwargs['orgid']
        pk = self.kwargs['pk']
        instance = get_object_or_404(self.queryset, name=pk, orgid=orgid)
        self.perform_destroy(instance)

        return processdata({
            "status": 0,
            "data": "",
            "msg": "delete vendor liasion success"
        }, request)


class VendorViewSet(viewsets.ModelViewSet):
    """
    API 供应商商处理函数
    """
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        self.queryset = Vendor.objects.filter(orgid=orgid)
        serializer = VendorSerializer(self.queryset, many=True)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def retrieve(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        pk = str(self.kwargs['pk']).upper()

        if not pk.isdigit():
            if pk not in ('ASSET', 'ISP', 'IDC'):
                return processdata({
                    "status": 0,
                    "data": '',
                    "msg": "传入数据错误"}, request)
            vendor = get_object_or_404(self.queryset, vendor_type=pk, orgid=orgid)
            serializer = VendorSerializer(vendor)
        else:
            vendor = get_object_or_404(self.queryset, id=pk, orgid=orgid)
            serializer = VendorSerializer(vendor)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""}, request)

    def create(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        request.data.update({'orgid': orgid})
        data = {"status": 0, "data": "", "msg": ""}

        if Vendor.objects.filter(name=request.data['name'], orgid=orgid).count():
            data['status'] = 1
            data['msg'] = '供应商已存在'
        else:
            serializer = VendorSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                self.perform_create(serializer)
                data['data'] = serializer.data
                content = '创建[%s]成功。' % request.query_params.get('name')
                cmdbinfo(orgid, '创建供应商成功', content)
            else:
                data['data'] = '验证失败，%s' % serializer.error
        return processdata(data, request)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        orgid = self.kwargs['orgid']
        pk = self.kwargs['pk']
        instance = get_object_or_404(self.queryset, id=pk, orgid=orgid)
        serializer = self.get_serializer(instance, request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        #   日志模式
        cmdbupdata(orgid, '供应商', Vendor.objects.filter(id=pk).first(), serializer.data)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def destroy(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        orgid = self.kwargs['orgid']
        pk = self.kwargs['pk']
        instance = get_object_or_404(self.queryset, id=pk, orgid=orgid)
        self.perform_destroy(instance)

        return processdata({
            "status": 0,
            "data": "",
            "msg": "删除供应商成功"
        }, request)


class IDCViewSet(viewsets.ModelViewSet):
    """
    IDC的增删改查
    """
    queryset = IDC.objects.all()
    serializer_class = IDCSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        self.queryset = IDC.objects.filter(orgid=orgid)
        serializer = IDCSerializer(self.queryset, many=True)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        orgid = self.kwargs['orgid']
        status = request.query_params.get('status', '0')
        if status == 0:
            idc = get_object_or_404(self.queryset, id=pk, orgid=orgid)
            serializer = IDCSerializer(idc)
        else:
            idc = get_object_or_404(self.queryset, vendor_id=pk, orgid=orgid)
            serializer = IDCSerializer(idc)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def create(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        request.data.update({'orgid': orgid})
        if IDC.objects.filter(name=request.data['name'], orgid=orgid).count() == 0:
            serializer = IDCSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return processdata({
                "status": 0,
                "data": "",
                "msg": "创建IDC成功"
            }, request)
        return processdata({
            "status": 1,
            "data": "",
            "msg": " 创建失败"
        }, request)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = self.kwargs['pk']  # idc的id
        orgid = self.kwargs['orgid']
        instance = get_object_or_404(self.queryset, id=pk, orgid=orgid)
        serializer = self.get_serializer(instance, request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def destroy(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = self.kwargs['pk']
        orgid = self.kwargs['orgid']
        instance = get_object_or_404(self.queryset, id=pk, orgid=orgid)
        self.perform_destroy(instance)

        return processdata({
            "status": 0,
            "data": "",
            "msg": "delete idc success"
        }, request)


class RackViewSet(viewsets.ModelViewSet):
    """
    API 对机柜的数据获取.
    """
    queryset = Rack.objects.all()
    serializer_class = RackSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        orgid = self.kwargs["orgid"]
        self.queryset = Rack.objects.filter(orgid=orgid)
        serializer = RackSerializer(self.queryset, many=True)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        orgid = self.kwargs["orgid"]
        status = request.query_params.get('status', '0')
        if status == '0':
            self.queryset = Rack.objects.filter(orgid=orgid, idc__id=pk)
        else:
            self.queryset = Rack.objects.filter(orgid=orgid, id=pk)
        serializer = RackSerializer(self.queryset, many=True)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def create(self, request, *args, **kwargs):
        orgid = self.kwargs["orgid"]
        request.data.update({"orgid": orgid})
        serializer = RackSerializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return processdata({
                "status": 0,
                "data": "",
                "msg": "成功创建机柜"
            }, request)
        return processdata({
            "status": 1,
            "data": "",
            "msg": "创建失败"
        }, request)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = self.kwargs["pk"]
        orgid = self.kwargs["orgid"]
        instance = get_object_or_404(self.queryset, id=pk, orgid=orgid)
        serializer = self.get_serializer(instance, request.data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return processdata({
                "status": 0,
                "data": serializer.data,
                "msg": ""
            }, request)
        return processdata({
            "status": 1,
            "data": "",
            "msg": "更新失败，%s" % serializer.error
        }, request)

    def destroy(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = self.kwargs["pk"]
        orgid = self.kwargs["orgid"]
        instance = get_object_or_404(self.queryset, id=pk, orgid=orgid)
        RackUnit.objects.filter(rack__id=pk, orgid=orgid).delete()
        self.perform_destroy(instance)
        return processdata({
            "status": 0,
            "data": "",
            "msg": "删除机柜成功"
        }, request)


class RackUnitViewSet(viewsets.ModelViewSet):
    """
    机柜使用信息
    """
    queryset = RackUnit.objects.all()
    serializer_class = RackUnitSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        self.queryset = RackUnit.objects.filter(orgid=orgid)
        serializer = RackUnitSerializer(self.queryset, many=True)

        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        orgid = self.kwargs['orgid']
        status = request.query_params.get('status', '0')
        if status == '0':
            self.queryset = RackUnit.objects.filter(orgid=orgid, id=pk)
        elif status == '1':
            self.queryset = RackUnit.objects.filter(orgid=orgid, rack__id=pk)
        serializer = RackUnitSerializer(self.queryset, many=True)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def create(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        request.data.update({'orgid': orgid})
        serializer = RackUnitSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return processdata({
                "status": 0,
                "data": serializer.data,
                "msg": "创建机柜使用信息成功"
            }, request)
        return processdata({
            "status": 1,
            "data": "",
            "msg": "创建机柜使用信息失败"
        }, request)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = self.kwargs['pk']
        orgid = self.kwargs['orgid']
        instance = get_object_or_404(self.queryset, id=pk, orgid=orgid)
        serializer = self.get_serializer(instance, request.data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return processdata({
                "status": 0,
                "data": serializer.data,
                "msg": ""
            }, request)
        return processdata({
            "status": 1,
            "data": "",
            "msg": "更新失败"
        }, request)

    def destroy(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = self.kwargs['pk']
        orgid = self.kwargs['orgid']
        instance = get_object_or_404(self.queryset, id=pk, orgid=orgid)
        self.perform_destroy(instance)
        return processdata({
            "status": 0,
            "data": "",
            "msg": "删除使用信息成功"
        }, request)


class IPSectionViewSet(viewsets.ModelViewSet):
    """
    API IP信息处理
    """
    queryset = IPSection.objects.all()
    serializer_class = IPSectionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']

        self.queryset = IPSection.objects.filter(orgid=orgid)
        serializer = IPSectionSerializer(self.queryset, many=True)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        orgid = self.kwargs['orgid']
        status = request.query_params.get('status', "0")
        iptype = request.query_params.get('iptype', 0)
        if status == '0':
            ips = get_object_or_404(self.queryset, id=pk, orgid=orgid)
        elif status == '1':  # 状态等于1情况，根据类型返回
            if iptype == 0:
                ips = get_object_or_404(self.queryset, idc__id=pk, orgid=orgid)
            else:
                ips = get_object_or_404(self.queryset, idc__id=pk, iptype=iptype, orgid=orgid)
        else:  # 状态等于2的情况下
            if iptype == 0:
                ips = get_object_or_404(self.queryset, iptype=pk, orgid=orgid)
            else:
                ips = get_object_or_404(self.queryset, orgid=orgid)
        serializer = IPSectionSerializer(ips)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def create(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        request.data.update({'orgid': orgid})
        data = {"status": 0, "data": "", "msg": ""}
        if IPSection.objects.filter(ips=request.data['ips'], orgid=orgid).count() == 0:
            serializer = IPSectionSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                self.perform_create(serializer)
                data['data'] = serializer.data
            else:
                data['status'] = 1
                data['msg'] = '数据验证失败,%s' % serializer.errors
        else:
            data['status'] = 1
            data['msg'] = '数据已存在'
        return processdata(data, request)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = self.kwargs['pk']
        orgid = self.kwargs['orgid']
        data = {"status": 0, "data": "", "msg": ""}
        instance = get_object_or_404(self.queryset, id=pk, orgid=orgid)
        serializer = self.get_serializer(instance, request.data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            data['data'] = serializer.data
        else:
            data['status'] = 1
            data['msg'] = '数据更新失败'
        return processdata(data, request)

    def destroy(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = self.kwargs['pk']
        orgid = self.kwargs['orgid']
        instance = get_object_or_404(self.queryset, id=pk, orgid=orgid)
        self.perform_destroy(instance)
        return processdata({
            "status": 0,
            "data": "",
            "msg": "删除数据成功"
        }, request)


class TagsViewSet(viewsets.ModelViewSet):
    """
    API 标签
    """
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        self.queryset = Tags.objects.filter(orgid=orgid)
        serializer = TagsSerializer(self.queryset, many=True)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        orgid = self.kwargs['orgid']
        tags = get_object_or_404(self.queryset, id=pk, orgid=orgid)
        serializer = TagsSerializer(tags)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def create(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        request.data.update({'orgid': orgid})
        data = {"status": 0, "data": "", "msg": ""}
        if Tags.objects.filter(name=request.data['name'], orgid=orgid).count() == 0:
            serializer = TagsSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                self.perform_create(serializer)
                data['data'] = serializer.data
            else:
                data['status'] = 1
                data['msg'] = '数据验证失败，%s' % serializer.errors
        else:
            data['status'] = 1
            data['msg'] = '数据已存在'
        return processdata({data, request})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = self.kwargs['pk']
        orgid = self.kwargs['orgid']
        data = {"status": 0, "data": "", "msg": ""}
        instance = get_object_or_404(self.queryset, pk=pk, orgid=orgid)
        serializer = self.get_serializer(instance, request.data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            data['data'] = serializer.data
        else:
            data['msg'] = '验证失败'
            data['status'] = 1
        return processdata(data, request)

    def destroy(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = self.kwargs['pk']
        orgid = self.kwargs['orgid']
        instance = get_object_or_404(self.queryset, pk=pk, orgid=orgid)
        self.perform_destroy(instance)
        return processdata({
            "status": 0,
            "data": "",
            "msg": "删除数据成功"
        }, request)


class CPUViewSet(viewsets.ModelViewSet):
    """
    CPU的处理
    """
    queryset = Cpu.objects.all()
    serializer_class = CpuSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        server_objs = Server.objects.filter(asset__orgid=orgid)
        self.queryset = Cpu.objects.filter(server_cpu__in=server_objs)
        serializer = CpuSerializer(self.queryset, many=True)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs['pk']  # 外键id
        status = request.query_params.get('status', '0')
        if status == '0':
            cpu = get_object_or_404(self.queryset, id=pk)
        elif status == '1':
            cpu = get_object_or_404(self.queryset, server__id=pk)
        else:
            cpu = get_object_or_404(self.queryset, sn=pk)
        serializer = CpuSerializer(cpu)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def create(self, request, *args, **kwargs):
        sn = self.request.data.get('sn')
        data = {"status": 0, "data": "", "msg": ""}
        # request.data.update({'server_cpu_id': server_cpu})
        if Cpu.objects.filter(server_cpu=request.data['server_cpu'], sn=sn).count() == 0:
            serializer = CpuSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                self.perform_create(serializer)
                data['data'] = serializer.data
            else:
                data['status'] = 1
                data['msg'] = '数据验证不通过，%s' % serializer.errors
        else:
            data['status'] = 1
            data['msg'] = '数据已存在'
        return processdata(data, request)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = self.kwargs['pk']  # 数据的id
        data = {"status": 0, "data": "", "msg": ""}
        instance = get_object_or_404(self.queryset, id=pk)
        serializer = self.get_serializer(instance, request.data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            data['data'] = serializer.data
        else:
            data['status'] = 1
            data['msg'] = '数据验证错误'
        return processdata(data, request)

    def destroy(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = self.kwargs['pk']  # 删除的id号
        instance = get_object_or_404(self.queryset, id=pk)
        self.perform_destroy(instance)
        return processdata({
            "status": 0,
            "data": "",
            "msg": "删除cpu成功"
        }, request)


class DiskViewSet(viewsets.ModelViewSet):
    """
    API 硬盘处理函数
    """
    queryset = Disk.objects.all()
    serializer_class = DiskSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        server_objs = Server.objects.filter(asset__orgid=orgid)
        self.queryset = Disk.objects.filter(server_disk__in=server_objs)
        serializer = DiskSerializer(self.queryset, many=True)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        orgid = self.kwargs['orgid']
        self.queryset = Disk.objects.filter(server_disk__asset__orgid=orgid)
        status = request.query_params.get('status', '0')
        server = request.query_params.get('server', '0')
        if status == '0':
            disk = get_object_or_404(self.queryset, id=pk)
        elif status == '1':  # 服务器筛选
            disk = get_object_or_404(self.queryset, server_disk_id=pk)
        elif status == '2':  # 硬盘类型筛选
            if server == '0':
                disk = get_object_or_404(self.queryset, disk_type=pk)
            else:
                server_obj = Server.objects.filter(id=server).first()
                disk = get_object_or_404(self.queryset, disk_type=pk, server_cpu=server_obj)
        else:  # 根据容量筛选
            disk = get_object_or_404(self.queryset, capacity=pk)
        serializer = DiskSerializer(disk)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": "Success"
        }, request)

    def create(self, request, *args, **kwargs):
        data = {"status": 0, "data": "", "msg": ""}
        serializer = DiskSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            data['data'] = serializer.data
        else:
            data['status'] = 1
            data['msg'] = '数据验证失败，%s' % serializer.errors
        return processdata(data, request)

    def update(self, request, *args, **kwargs):
        data = {"status": 0, "data": "", "msg": ""}
        partial = kwargs.pop('partial', False)
        instance = get_object_or_404(self.queryset)
        serializer = self.get_serializer(instance, request.data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            data['data'] = serializer.data
        else:
            data['status'] = 1
            data['msg'] = '数据验证失败，%s' % serializer.errors
        return processdata(data, request)

    def destroy(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = self.kwargs['pk']
        instance = get_object_or_404(self.queryset, id=pk)
        self.perform_destroy(instance)

        return processdata({
            "status": 0,
            "data": "",
            "msg": "删除硬盘成功"
        }, request)


class NICViewSet(viewsets.ModelViewSet):
    """
    API 网卡处理函数
    """
    queryset = NIC.objects.all()
    serializer_class = NICSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        self.queryset = NIC.objects.filter(server_nic__asset__orgid=orgid)
        serializer = NICSerializer(self.queryset, many=True)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs['pk']  # 可以多一个条件，/pk/
        orgid = self.kwargs['orgid']
        status = request.query_params.get('status', '0')
        self.queryset = NIC.objects.filter(server_nic__asset__orgid=orgid)
        if status == '0':
            nic = get_object_or_404(self.queryset, id=pk)
        elif status == '1':
            nic = get_object_or_404(self.queryset, server_nic__id=pk)
        else:
            return processdata({"status": 0, "data": "", "msg": "条件错误"}, request)
        serializer = NICSerializer(nic)
        return processdata({"status": 0, "data": serializer.data, "msg": ""}, request)

    def create(self, request, *args, **kwargs):
        data = {"status": 0, "data": "", "msg": ""}
        serializer = NICSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            data['data'] = serializer.data
        else:
            data['status'] = 1
            data['msg'] = '数据验证错误，%s' % serializer.errors
        return processdata(data, request)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = self.kwargs['pk']
        data = {"status": 0, "data": "", "msg": ""}
        instance = get_object_or_404(self.queryset, id=pk)
        serializer = self.get_serializer(instance, request.data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            data['data'] = serializer.data
        else:
            data['status'] = 1
            data['msg'] = '验证不通过，%s' % serializer.errors
        return processdata(data, request)

    def destroy(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = self.kwargs['pk']
        instance = get_object_or_404(self.queryset, id=pk)
        self.perform_destroy(instance)

        return processdata({
            "status": 0,
            "data": "",
            "msg": "删除网卡成功"
        }, request)


class MemoryViewSet(viewsets.ModelViewSet):
    """
    API 内存处理函数
    """
    queryset = Memory.objects.all()
    serializer_class = MemorySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        self.queryset = Memory.objects.filter(server_mem__asset__orgid=orgid)
        serializer = MemorySerializer(self.queryset, many=True)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def retrieve(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        pk = self.kwargs['pk']  # 获取某个服务器下的内存信息
        condition = request.query_params.get('condition')
        self.queryset = Memory.objects.filter(server_mem__asset__orgid=orgid)
        if pk == '0':
            mem = get_object_or_404(self.queryset, id=condition)
        elif pk == '1':  # 获取某型号的所有内存
            mem = get_object_or_404(self.queryset, model=condition)
        elif pk == '2':  # 获取某空间大小的所有内存
            mem = get_object_or_404(self.queryset, capacity=condition)
        else:
            return processdata({
                "status": 0,
                "data": "",
                "msg": "条件不匹配"
            }, request)
        serializer = MemorySerializer(mem)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def create(self, request, *args, **kwargs):
        serializer = MemorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return processdata({
            "status": 0,
            "data": "",
            "msg": "创建内存成功"
        }, request)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = self.kwargs['pk']
        instance = get_object_or_404(self.queryset)
        serializer = self.get_serializer(instance, request.data, id=pk, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": "success"
        }, request)

    def destroy(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = self.kwargs['pk']
        instance = get_object_or_404(self.queryset, id=pk)
        self.perform_destroy(instance)

        return processdata({
            "status": 0,
            "data": "",
            "msg": "删除网卡成功"
        }, request)


class PlansViewSet(viewsets.ModelViewSet):
    """
    API 套餐处理函数
    """
    queryset = Plans.objects.all()
    serializer_class = PlanSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        # server = request.query_params.get('server')
        data = {"status": 0, "data": {}, "msg": ""}
        self.queryset = Plans.objects.filter(orgid=orgid)
        # if server:
        #     serverqueryset = Server.objects.filter(orgid=orgid, plans__in=self.queryset)
        #     serverserializer = ServerSerializer(serverqueryset, many=True)
        #     data['data']['server'] = serverserializer.data
        serializer = PlanSerializer(self.queryset, many=True)
        data['data']['plans'] = serializer.data
        return processdata(data, request)

    def retrieve(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        pk = self.kwargs['pk']
        server = request.query_params.get('server',False)
        data = {"status": 0, "data": {}, "msg": ""}
        queryset = Plans.objects.filter(orgid=orgid, id=pk)
        if server and queryset:
            server_queryset = PlansServer.objects.filter(orgid=orgid, plans=queryset.first())
            server_serializer = ServerSerializer(server_queryset, many=True)
            data['data']['server'] = server_serializer.data
        serializer = PlanSerializer(queryset, many=True)
        data['data']['plans'] = serializer.data
        return processdata(data, request)

    def create(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        request.data.update({'orgid': orgid})
        if Plans.objects.filter(name=request.data['name'], orgid=orgid).count() == 0:
            serializer = PlanSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return processdata({
                "status": 0,
                "data": "",
                "msg": "创建套餐成功"
            }, request)
        return processdata({
            "status": 1,
            "data": "",
            "msg": "创建套餐失败"
        }, request)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        orgid = self.kwargs['orgid']
        pk = self.kwargs['pk']
        instance = get_object_or_404(self.queryset, name=pk, orgid=orgid)
        serializer = self.get_serializer(instance, request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def destroy(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        orgid = self.kwargs['orgid']
        pk = self.kwargs['pk']
        instance = get_object_or_404(self.queryset, id=pk, orgid=orgid)
        self.perform_destroy(instance)

        return processdata({
            "status": 0,
            "data": "",
            "msg": "删除套餐成功"
        }, request)


class PSViewSet(viewsets.ModelViewSet):
    """
    API 套餐和服务器关联接口
    """
    queryset = PlansServer.objects.all()
    serializer_class = PSSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        self.queryset = PlansServer.objects.filter(orgid=orgid)
        serializer = PSSerializer(self.queryset, many=True)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def retrieve(self, request, *args, **kwargs):
        orgid = self.kwargs['orgid']
        pk = self.kwargs['pk']
        data = request.query_params.get('data')
        self.queryset = PlansServer.objects.filter(orgid=orgid)
        if pk == '0':  # 套餐关联的服务器
            ps_data = get_object_or_404(self.queryset, plans=data)
        elif pk == '1':  # 服务器关联的套餐
            ps_data = get_object_or_404(self.queryset, server=data)
        else:
            return processdata({
                "status": 0,
                "data": "",
                "msg": "条件不匹配"
            }, request)
        serializer = PSSerializer(ps_data)
        return processdata({
            "status": 0,
            "data": serializer.data,
            "msg": ""
        }, request)

    def create(self, request, *args, **kwargs):
        data = {"status": 0, "data": "", "msg": ""}
        serializer = PSSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            data['data'] = serializer.data
        else:
            data['status'] = 1
            data['msg'] = '数据验证失败，%s' % serializer.errors
        return processdata(data, request)

    def update(self, request, *args, **kwargs):
        data = {"status": 0, "data": "", "msg": ""}
        partial = kwargs.pop('partial', False)
        pk = self.kwargs['pk']
        instance = get_object_or_404(self.queryset)
        serializer = self.get_serializer(instance, request.data, id=pk, partial=partial)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            data['data'] = serializer.data
        else:
            data['status'] = 1
            data['msg'] = '数据验证失败，%s' % serializer.errors
        return processdata(data, request)

    def destroy(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = self.kwargs['pk']
        instance = get_object_or_404(self.queryset, id=pk)
        self.perform_destroy(instance)

        return processdata({
            "status": 0,
            "data": "",
            "msg": "删除成功"
        }, request)
