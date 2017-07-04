from rest_framework import serializers
from repository.models import *
from utils.functools import ipverification,ctime,macverification


class LiaisonSerializer(serializers.ModelSerializer):
    def validate(self, data):
        """
        数据验证
        """
        print(data)
        if not data.get('orgid'):
            raise serializers.ValidationError('没有所属id号')
        if data['orgid']:
            if not str(data['orgid']).isdigit():
                raise serializers.ValidationError('所属ID类型错误')

        return data

    def create(self, validated_data):
        return Liasion.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.position = validated_data.get('position', instance.position)
        instance.work_content = validated_data.get('work_content', instance.work_content)
        instance.save()

        return instance

    class Meta:
        model = Liasion
        fields = '__all__'


class VendorSerializer(serializers.ModelSerializer):
    def validate(self, data):
        """
        Check
        """
        if data['orgid']:
            if not str(data['orgid']).isdigit():
                raise serializers.ValidationError('所属ID类型错误')
        return data

    def create(self, validated_data):
        return Vendor.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.description = validated_data.get('description', instance.description)
        instance.address = validated_data.get('address', instance.address)
        instance.save()

        return instance

    class Meta:
        model = Vendor
        fields = '__all__'


class IDCSerializer(serializers.ModelSerializer):
    def validate(self, data):
        """
        数据验证
        """
        if not data['name'] or not data['orgid']:
            raise serializers.ValidationError("必须包含所属id和名称")
        if not data['vendor']:
            raise serializers.ValidationError('厂商错误')
        if data['orgid']:
            if not str(data['orgid']).isdigit():
                raise serializers.ValidationError('所属ID类型错误')
        if data['vendor']:
            if not Vendor.objects.filter(id=data['vendor']):
                raise serializers.ValidationError('供应商错误')

        return data

    def create(self, validated_data):
        return IDC.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.description = validated_data.get('description', instance.description)
        instance.name = validated_data.get('name', instance.name)
        instance.address = validated_data.get('address', instance.address)
        instance.vendor = validated_data.get('vendor', instance.vendor)
        instance.save()

        return instance

    class Meta:
        model = IDC
        fields = '__all__'


class RackSerializer(serializers.ModelSerializer):
    def validate(self, data):
        """
        机房数据验证
        """
        if not data['name'] or not data['max_units'] or not data['orgid']:
            raise serializers.ValidationError("必须包含名称，最大U位，和所属ID")

        if not data['idc']:
            raise serializers.ValidationError("Must have idc field")
        elif IDC.objects.filter(name=data['idc'], orgid=data['orgid']).count() == 0:
            raise serializers.ValidationError("IDC选择错误")

        return data

    def create(self, validated_data):
        return Rack.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.description = validated_data.get('description', instance.description)
        instance.power_capacity = validated_data.get('power_capacity', instance.power_capacity)
        instance.max_units = validated_data.get('max_units', instance.max_units)
        instance.idc = validated_data.get('idc', instance.idc)
        instance.room = validated_data.get('room', instance.room)
        instance.save()

        return instance

    class Meta:
        model = Rack
        fields = '__all__'


class RackUnitSerializer(serializers.ModelSerializer):
    def validate(self, data):
        """
       机柜详细信息
        """
        if data['asset']:
            if RackUnit.objects.filter(asset=data['asset']):
                raise serializers.ValidationError('资产已经存放，不能新建')

        if not data['rack'] or not data['unit_number'] or not data['orgid']:
            raise serializers.ValidationError("必须有机柜、编号和所属id")
        if data['rack']:
            nub = RackUnit.objects.filter(rack=data['rack']).count()
            max_unit = data['rack'].max_units
            if nub*2 + data['asset'].unit + 1 > max_unit:
                raise serializers.ValidationError('此机柜的数量U位不足')
        if data['unit_number']:
            data['unit_number'] = int(data['unit_number'])
            if data['unit_number'] <= nub*2 or data['unit_number'] > 48:
                raise serializers.ValidationError('输入数字不符合实际')
        return data

    def create(self, validated_data):
        return RackUnit.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        return instance

    class Meta:
        model = RackUnit
        exclude = ('id',)


class IPSectionSerializer(serializers.ModelSerializer):
    def validate(self, data):
        """
        IP地址数据验证
        """
        if not data['rack'] or not data['orgid'] or not data['ips']:
            raise serializers.ValidationError("必须包含所属id/rack/ips外键")

        if data['ips']:
            ret = ipverification(data['ips'])
            if not ret:
                raise serializers.ValidationError('ip地址格式不对')

        return data

    def create(self, validated_data):
        return IPSection.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.gateway = validated_data.get('gateway', instance.gateway)
        instance.description = validated_data.get('description', instance.description)
        instance.idc = validated_data.get('idc', instance.idc)
        instance.mask = validated_data.get('mask', instance.mask)
        instance.isp = validated_data.get('isp', instance.isp)
        instance.orgid = validated_data.get('orgid', instance.orgid)
        instance.iptype = validated_data.get('iptype', instance.iptype)
        instance.save()

        return instance

    class Meta:
        model = IPSection
        fields = '__all__'


class TagsSerializer(serializers.ModelSerializer):
    def validate(self, data):
        """
        IP地址数据验证
        """
        if not data['orgid'] or not data['name']:
            raise serializers.ValidationError('缺失所属id和标签名称')
        if data['orgid']:
            try:
                int(data['orgid'])
            except ValueError as e:
                raise serializers.ValidationError('orgid必须是数字')
        if data['name']:
            if Tags.objects.filter(orgid=data['orgid'],name=data['name']).count():
                raise serializers.ValidationError('数据重复')
        return data

    def create(self, validated_data):

        return Tags.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.orgid = validated_data.get('orgid', instance.orgid)
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        return instance

    class Meta:
        model = Tags
        fields = '__all__'


class CpuSerializer(serializers.ModelSerializer):
    def validate(self, data):
        """
        CPU数据验证
        """
        if not data['sn']:
            raise serializers.ValidationError('必须包含sn编号')
        if not data['server_cpu']:
            raise serializers.ValidationError("必须包含外键关联服务器")
        if data['sn'] and data['server_cpu']:
            obj = Cpu.objects.filter(server_cpu_id=data['server_cpu'], sn=data['sn'])
            if obj:
                raise serializers.ValidationError('sn已存在')
        if not data['manufacturer']:
            raise serializers.ValidationError('必须包含制造商')
        if not data['model']:
            raise serializers.ValidationError('必须包含型号')
        return data

    def create(self, validated_data):
        print(validated_data)
        cpu_obj = Cpu.objects.create(**validated_data)
        return cpu_obj

    def update(self, instance, validated_data):
        instance.manufacturer = validated_data.get('manufacturer', instance.manufacturer)
        instance.model = validated_data.get('model', instance.model)
        instance.frequency = validated_data.get('frequency', instance.frequency)
        instance.save()

        return instance

    class Meta:
        model = Cpu
        fields = "__all__"


class DiskSerializer(serializers.ModelSerializer):
    def validate(self, data):
        """
        硬盘数据验证
        """
        if not data['server_disk']:
            raise serializers.ValidationError("必须属于某个服务器")

        if data['server_disk']:
            if not Server.objects.filter(id=data['server_disk'].id):
                raise serializers.ValidationError("服务器不存在")

        if not data['capacity']:
            raise serializers.ValidationError('磁盘大小不能为空')
        if data['capacity']:
            try:
                data['capacity'] = int(data['capacity'])
            except Exception as e:
                raise serializers.ValidationError('必须是数字格式')
        print('验证硬盘数据')
        return data

    def create(self, validated_data):
        disk_obj = Disk.objects.create(**validated_data)
        return disk_obj

    def update(self, instance, validated_data):
        instance.disk_type = validated_data.get('disk_type', instance.disk_type)
        instance.model = validated_data.get('model', instance.model)
        instance.capacity = validated_data.get('capacity', instance.capacity)
        instance.slot = validated_data.get('slot', instance.slot)
        instance.save()

        return instance

    class Meta:
        model = Disk
        fields = "__all__"


class NICSerializer(serializers.ModelSerializer):
    def validate(self, data):
        """
        网卡审核
        """
        if not data['name']:
            raise serializers.ValidationError("必须包含网卡名称")

        if not data['mac']:
            raise serializers.ValidationError("没有mac地址")
        if data['mac']:
            ret = macverification(data['mac'])
            if not ret:
                raise serializers.ValidationError('mac格式地址错误')
            else:
                data['mac'] = ret
        if data['netmask']:
            ret = ipverification(data['netmask'])
            if not ret:
                raise serializers.ValidationError('网关格式地址错误')
        if data['ipaddrs']:
            ret = ipverification(data['ipaddrs'])
            if not ret:
                raise serializers.ValidationError('IP地址格式地址错误')
        if data['gateway'] and data['ipaddrs']:
            ret = ipverification(data['gateway'])
            if not ret:
                raise serializers.ValidationError('网关地址格式错误')
            # ret = 0
            # for i,v in enumerate(data['gateway']):
            #     if v == data['ipaddrs'][i]:
            #         ret += 1
            # if ret <= 5:
            #     raise serializers.ValidationError('网关与IP不匹配')
        return data

    def create(self, validated_data):
        nic_obj = NIC.objects.create(**validated_data)
        return nic_obj

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.gateway = validated_data.get('gateway', instance.gateway)
        instance.netmask = validated_data.get('netmask', instance.netmask)
        instance.ipaddrs = validated_data.get('ipaddrs', instance.ipaddrs)
        instance.save()

        return instance

    class Meta:
        model = NIC
        fields = "__all__"


class MemorySerializer(serializers.ModelSerializer):
    def validate(self, data):
        """
        内存验证
        """
        if not data['sn']:
            raise serializers.ValidationError("必须填写内存sn号")
        if not data['capacity']:
            raise serializers.ValidationError('必须填写内存容量')
        if data['server_mem']:
            if not Server.objects.filter(id=data['server_mem'].id):
                raise serializers.ValidationError('服务器关联失败')
        if data['vendor']:
            if not Vendor.objects.filter(id=data['vendor'].id):
                raise serializers.ValidationError("供应商不匹配")

        if data['capacity']:
            try:
                data['capacity'] = int(data['capacity'])
            except Exception as e:
                raise serializers.ValidationError('内存大小填写错误')

        return data

    def create(self, validated_data):
        memory_obj = Memory.objects.create(**validated_data)
        return memory_obj

    def update(self, instance, validated_data):
        instance.slot = validated_data.get('slot', instance.slot)
        instance.rate = validated_data.get('rate', instance.rate)
        instance.save()

        return instance

    class Meta:
        model = Memory
        fields = "__all__"


class PlanSerializer(serializers.ModelSerializer):
    def validate(self, data):
        """
        套餐验证
        """
        if not data['orgid'] or not data['name']:
            raise serializers.ValidationError('必须包含所属ID和名称')
        if data['orgid']:
            if not str(data['orgid']).isdigit():
                raise serializers.ValidationError('所属ID类型错误')
        if data['orgid'] and data['name']:
            if Plans.objects.filter(orgid=data['orgid'], name=data['name']).count():
                raise serializers.ValidationError('套餐已经存在')
        return data

    def create(self, validated_data):
        return Plans.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.description = validated_data.get('description', instance.description)
        instance.name = validated_data.get('name', instance.name)
        instance.cpu = validated_data.get('cpu', instance.cpu)
        instance.mem = validated_data.get('mem', instance.mem)
        instance.disk = validated_data.get('disk', instance.disk)
        instance.save()

        return instance

    class Meta:
        model = Plans
        fields = '__all__'


class PSSerializer(serializers.ModelSerializer):
    def validate(self, data):
        """
        套餐验证
        """
        if not data['orgid']:
            raise serializers.ValidationError('所属id不能为空')
        if not data['server'] or not data['plans']:
            raise serializers.ValidationError('数据错误')
        return data

    def create(self, validated_data):
        return PlansServer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.plans = validated_data.get('plans', instance.plans)
        instance.server = validated_data.get('server', instance.server)
        instance.save()

        return instance

    class Meta:
        model = PlansServer
        fields = '__all__'


class AssetSerializer(serializers.ModelSerializer):
    def validate(self, data):
        """
        资产验证
        """
        if not data['orgid'] or not data['sn'] or not data['product_name']:
            raise serializers.ValidationError('缺少所属id或sn号或产品型号')
        if data['orgid']:
            if not str(data['orgid']).isdigit():
                raise serializers.ValidationError('所属id不正确')
        if data['sn'] and Asset.objects.filter(orgid=data['orgid'],sn=data['sn'],product_name=data['product_name']).count():
            raise serializers.ValidationError('sn已存在')
        if not data['vendor']:
            raise serializers.ValidationError('没有选择厂商')
        if data['vendor']:
            print(data['vendor'])
            ret = Vendor.objects.filter(id=data['vendor'].id).count()
            if not ret:
                raise serializers.ValidationError('厂商不正确')
        if data['manage_ip']:
            ret = ipverification(data['manage_ip'])
            if not ret:
                raise serializers.ValidationError('管理ip格式不正确')
        if not data['unit']:
            raise serializers.ValidationError('设备U位不正确')
        if data['unit']:
            if str(data['unit']).isdigit():
                ret = int(data['unit'])
                if ret < 1 or ret > 47:
                    raise serializers.ValidationError('资产U位不正确')
        if data['latest_date'] or not data['latest_date']:
            data['latest_date'] = ctime('time')
        return data

    def create(self, validated_data):
        tags = validated_data.get('tags')
        del validated_data['tags']
        obj = Asset.objects.create(**validated_data)
        if tags:
            tags_objs = Tags.objects.filter(id__in=tags)
            obj.tags.add(*tags_objs)
        return obj

    def update(self, instance, validated_data):
        if validated_data.get('tags'):
            tags = validated_data['tags']
            del validated_data['tags']
            tags_objs = Tags.objects.filter(id__in=tags)
            instance.tags.set(*tags_objs)
        instance.device_status = validated_data.get('device_status', instance.device_status)
        instance.manage_ip = validated_data.get('manage_ip', instance.manage_ip)
        instance.latest_date = validated_data.get('latest_date', instance.latest_date)

        tags = validated_data.get('tags')
        tags_objs = Tags.objects.filter(id__in=tags)
        instance.tags = tags_objs
        instance.save()

        return instance

    class Meta:
        model = Asset
        fields = '__all__'


class ServerSerializer(serializers.ModelSerializer):
    def validate(self, data):
        """
        服务器验证
        """
        if not data['asset']:
            raise serializers.ValidationError('资产不能为空')
        if data['asset']:
            if not Asset.objects.filter(id=data['asset'].id):
                raise serializers.ValidationError('资产不存在')
        if data['int_ip']:
            ret = ipverification(data['int_ip'])
            if not ret:
                raise serializers.ValidationError('内网IP地址格式错误')
        if data['ext_ip']:
            ret = ipverification(data['ext_ip'])
            if not ret:
                raise serializers.ValidationError('外网IP地址格式错误')
        return data

    def create(self, validated_data):
        return Server.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.hostname = validated_data.get('hostname', instance.hostname)
        instance.raid = validated_data.get('raid', instance.raid)
        instance.os_platform = validated_data.get('os_platform', instance.os_platform)
        instance.os_version = validated_data.get('os_version', instance.os_version)
        instance.int_ip = validated_data.get('int_ip', instance.int_ip)
        instance.ext_ip = validated_data.get('ext_ip', instance.ext_ip)
        instance.note = validated_data.get('note', instance.note)
        instance.save()

        return instance

    class Meta:
        model = Server
        fields = '__all__'


class NetworkSerializer(serializers.ModelSerializer):
    def validate(self, data):
        """
        服务器验证
        """
        if data['asset'].device_type == 'SERVER':
            raise serializers.ValidationError('资产类型不符合。')
        if data['int_ip']:
            ret = ipverification(data['int_ip'])
            if not ret:
                raise serializers.ValidationError('内网IP地址格式错误')
        if data['ext_ip']:
            ret = ipverification(data['ext_ip'])
            if not ret:
                raise serializers.ValidationError('外网IP地址格式错误')
        if data['port_num']:
            if not str(data['port_num']).isdigit():
                raise serializers.ValidationError('端口必须是数字')

        return data

    def create(self, validated_data):
        return NetworkDevice.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.device_type = validated_data.get('device_type', instance.device_type)
        instance.int_ip = validated_data.get('int_ip', instance.int_ip)
        instance.ext_ip = validated_data.get('ext_ip', instance.ext_ip)
        instance.port_num = validated_data.get('port_num', instance.port_num)
        instance.device_detail = validated_data.get('device_detail', instance.device_detail)
        instance.note = validated_data.get('note', instance.note)

        instance.save()

        return instance

    class Meta:
        model = NetworkDevice
        fields = '__all__'