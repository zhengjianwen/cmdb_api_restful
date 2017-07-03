from django.db import models
from model_utils.fields import StatusField
from model_utils import Choices
from utils.RYModel import ModelDiffMixin


class Liasion(models.Model):
    """
    联系信息表
    """
    orgid = models.CharField(u'所属ID', max_length=24)
    name = models.CharField(u'姓名', max_length=32)
    phone = models.CharField(u'电话', max_length=15, null=True, blank=True)
    position = models.CharField(u'职务', max_length=64)
    work_content = models.CharField(u'负责内容', max_length=128)
    vendor = models.ForeignKey('Vendor')

    class Meta:
        unique_together = ('orgid', 'vendor', 'phone')
        verbose_name_plural = u'联系信息表'

    def __str__(self):
        return '%s-%s-%s' % (self.vendor, self.name, self.phone)


class Vendor(models.Model):
    """
    供应商信息
    """
    type_choices = Choices('ISP', 'ASSET', 'IDC',)
    vendor_type = StatusField(choices_name='type_choices', verbose_name='供应商类型')
    orgid = models.CharField(u'所属ID', max_length=24)
    name = models.CharField(u'厂商名称', max_length=64)
    address = models.CharField(u'联系地址', max_length=255, null=True, blank=True)
    note = models.CharField(u'备注', max_length=128, null=True, blank=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        unique_together = ('name', 'orgid', 'vendor_type')
        verbose_name_plural = u'供应商信息表'


class IDC(models.Model):
    """
    IDC机房信息表
    """
    orgid = models.CharField(u'所属ID', max_length=24)
    name = models.CharField(u'IDC机房名称', max_length=15)
    address = models.CharField(u'地址', max_length=128, null=True, blank=True)
    description = models.CharField(u'IDC描述信息', max_length=128, null=True)
    vendor = models.ForeignKey('Vendor', verbose_name='厂商')

    def __str__(self):
        return "%s" % self.name

    class Meta:
        unique_together = ('name', 'orgid')
        verbose_name_plural = u'IDC信息表'


class Rack(models.Model):
    """
    机柜信息表
    """
    orgid = models.CharField(u'所属ID', max_length=24)
    idc = models.ForeignKey('IDC', verbose_name=u'所属机房')
    room = models.CharField(u'房间号', max_length=18, null=True, blank=True)
    name = models.CharField(u'机柜名称', max_length=32)
    power_capacity = models.CharField(u'功率容量', max_length=32, null=True, blank=True)
    max_units = models.SmallIntegerField(u'最大U位')
    description = models.CharField(u'机柜描述', max_length=128, null=True, blank=True)

    def __str__(self):
        return "%s机房房间%s-%s" % (self.idc, self.room, self.name)

    class Meta:
        unique_together = ('name', 'orgid')
        verbose_name_plural = u'机柜信息表'


class RackUnit(models.Model):
    """
    机柜U位使用表
    """
    asset = models.OneToOneField('Asset')
    orgid = models.CharField(u'所属ID', max_length=24)
    rack = models.ForeignKey('Rack', verbose_name=u'所属机柜', max_length=24)
    unit_number = models.SmallIntegerField(u'机架号')

    class Meta:
        unique_together = ('orgid', 'rack', 'unit_number')
        verbose_name_plural = u'机柜使用表'


class IPSection(models.Model):
    """
    所有IP信息表
    """
    type_choices = Choices('EXT', 'INT')
    orgid = models.CharField(u'所属ID', max_length=24)
    idc = models.ForeignKey(u'IDC', null=True, blank=True)
    iptype = StatusField(u'类型', choices_name='type_choices')
    ips = models.GenericIPAddressField(u'IP地址', null=True, blank=True)
    mask = models.GenericIPAddressField(u'子网掩码', null=True, blank=True)
    gateway = models.GenericIPAddressField(u'网关', null=True, blank=True)
    description = models.CharField(u'描述', max_length=64, null=True, blank=True)

    verdor = models.ForeignKey('Vendor', verbose_name=u'运行商', null=True, blank=True)

    def __str__(self):
        return "%s" % self.ips

    class Meta:
        unique_together = ('ips', 'orgid', 'idc')
        verbose_name_plural = '网段信息表'


class Tags(models.Model):
    """
    标签表
    """
    orgid = models.CharField(u'所属ID', max_length=24)
    name = models.CharField('名称', max_length=32)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['orgid', 'name']


class Asset(models.Model):
    """
    资产信息表，所有资产信息（服务器，网络设备）
    """
    type_choices = Choices('SERVER', 'NETWORK')
    status_choices = Choices('RUNNING', 'MAINTANCING', 'STOCK')

    orgid = models.CharField(u'所属ID', max_length=24)
    device_type = StatusField(u'资产类型', choices_name='type_choices', null=True, blank=True)
    device_status = StatusField(u'资产状态', choices_name='status_choices', null=True, blank=True)
    vendor = models.ForeignKey('Vendor', verbose_name=u'供应商')
    sn = models.CharField(u'SN号', max_length=64, db_index=True)
    product_name = models.CharField(u'产品型号', max_length=64, null=True, blank=True)
    manage_ip = models.GenericIPAddressField(u'管理IP', max_length=64, blank=True, null=True)
    unit = models.SmallIntegerField('机器U数')
    latest_date = models.DateTimeField(u'最新更新日期', null=True)
    create_at = models.DateField(u'采购日期', null=True)
    tags = models.ManyToManyField('Tags', blank=True)

    class Meta:
        unique_together = ('orgid', 'sn', 'product_name')
        verbose_name_plural = u"资产表"

    def __str__(self):
        return '%s-%s-%s' % (self.orgid, self.device_type, self.product_name)


class Server(models.Model):
    """
    服务器信息
    """
    raid_choices = Choices('RAID5', 'RAID0', 'RAID1', 'RAID10', 'RAID6', 'DIRECT')
    type_choices = Choices('CLOUD', 'ENTITY', 'VMSYSTEM')
    asset = models.OneToOneField('Asset')

    s_type = StatusField('服务器类型', choices_name='type_choices')
    hostname = models.CharField(u'主机名称', max_length=128, unique=True)
    raid = StatusField(u'raid卡', choices_name='raid_choices', null=True, blank=True)
    os_platform = models.CharField(u'系统', max_length=16, null=True, blank=True)
    os_version = models.CharField(u'系统版本', max_length=16, null=True, blank=True)
    int_ip = models.GenericIPAddressField(u'内网IP', max_length=64, blank=True, null=True)
    ext_ip = models.GenericIPAddressField(u'外网IP', max_length=64, blank=True, null=True)
    note = models.CharField(u'备注', max_length=128, null=True, blank=True)
    create_at = models.DateField(u'创建时间', blank=True)

    class Meta:
        verbose_name_plural = u"服务器表"

    def __str__(self):
        return '%s - %s' % (self.asset, self.hostname)


class NetworkDevice(models.Model):
    """
    网络设备表
    """
    type_choices = Choices('SWITCH', 'FIREWALL', 'ROUTER', 'OTHER')
    asset = models.OneToOneField('Asset')
    device_type = StatusField(u'设备类型', choices_name='type_choices')
    vlan_ip = models.CharField(u'VlanIP', max_length=64, blank=True, null=True)
    intranet_ip = models.CharField(u'内网IP', max_length=128, blank=True, null=True)
    port_num = models.SmallIntegerField(u'端口个数', null=True, blank=True)
    device_detail = models.CharField(u'设置详细配置', max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = u"网络设备"

    def __str__(self):
        return '%s-%s' % (self.device_type, self.asset.product_name)


class Cpu(models.Model):
    """
    CPU信息
    """
    status_choices = Choices('RUNNING', 'MAINTANCING', 'DOWN', 'STOCK')
    manufacturer_choices = Choices('Intel', 'AMD', 'IBM', 'IDT')

    server_cpu = models.ForeignKey('Server', related_name='CPU')
    sn = models.CharField(u'sn编号', max_length=32,db_index=True)
    manufacturer = StatusField(u'制造商', choices_name='manufacturer_choices')
    model = models.CharField(u'型号', max_length=64)
    frequency = models.CharField(u'主频', max_length=16, null=True, blank=True)

    class Meta:
        verbose_name_plural = u"CPU信息表"

    def __str__(self):
        return '%s - %s%s' % (self.server_cpu, self.manufacturer, self.model)


class Disk(models.Model):
    """
    硬盘信息
    """
    disk_type_choices = Choices('SATA', 'SSD', 'SAS', 'SCSI', 'IDE')
    status_choices = Choices('RUNNING', 'MAINTANCING', 'DOWN', 'STOCK')

    server_disk = models.ForeignKey('Server', related_name='disk')
    disk_type = StatusField(u'磁盘类型', choices_name='disk_type_choices', null=True)
    model = models.CharField(u'磁盘型号', max_length=32, null=True, blank=True)
    capacity = models.FloatField(u'磁盘容量GB', blank=True)
    slot = models.CharField(u'插槽位', max_length=8, null=True, blank=True)

    class Meta:
        verbose_name_plural = u"硬盘表"

    def __str__(self):
        return '%s- %s-%s' % (self.server_disk, self.server_disk, self.slot)


class NIC(models.Model):
    """
    网卡信息
    """
    server_nic = models.ForeignKey('Server', related_name='nic')

    name = models.CharField(u'网卡名称', max_length=128, blank=True)
    model = models.CharField(u'网卡型号', max_length=128, null=True, blank=True)
    mac = models.CharField(u'网卡MAC地址', db_index=True, max_length=64, blank=True)
    ipaddrs = models.GenericIPAddressField(u'ip地址', max_length=64, null=True, blank=True)
    netmask = models.GenericIPAddressField(u'掩码', max_length=64, null=True, blank=True)
    gateway = models.GenericIPAddressField(u'网关', max_length=64, null=True, blank=True)
    note = models.CharField(u'备注', max_length=64, null=True)

    class Meta:
        verbose_name_plural = u"网卡表"
        unique_together = ('name', 'mac')

    def __str__(self):
        return '%s-%s' % (self.server_nic, self.name)


class Memory(models.Model):
    """
    内存信息
    """
    server_mem = models.ForeignKey('Server', related_name='memory')
    sn = models.CharField(u'内存SN号', max_length=64, blank=True, db_index=True)
    vendor = models.ForeignKey('Vendor', verbose_name='制造商', null=True, blank=True)
    model = models.CharField(u'型号', max_length=64, null=True)
    capacity = models.FloatField(u'容量G', blank=True)
    rate = models.CharField(u'速率', max_length=16, null=True, blank=True)
    slot = models.CharField(u'插槽位', max_length=32, null=True)

    class Meta:
        verbose_name_plural = u"内存表"

    def __str__(self):
        return '%s - %s - %s' % (self.server_mem, self.slot, self.capacity)


class Plans(models.Model):
    """
    套餐表
    """
    # id = models.IntegerField(db_index=True, primary_key=True)
    orgid = models.CharField(u'所属ID', max_length=24)
    name = models.CharField(u'套餐名称', max_length=15, db_index=True, unique=True)
    cpu = models.SmallIntegerField('cpu核数', default=1)
    mem = models.IntegerField('内存大小GB', default=1)
    disk = models.IntegerField('磁盘大小GB', default=100)
    description = models.CharField(u'描述', max_length=64, null=True, blank=True)
    server = models.ManyToManyField('Server', through='PlansServer', verbose_name='关联服务器', blank=True)

    def __str__(self):
        return "%s-%s - %s" % (self.orgid, self.name,self.description)

    class Meta:
        unique_together = ('name', 'orgid')
        verbose_name_plural = u'套餐信息'


class PlansServer(models.Model):
    orgid = models.CharField(u'所属ID', max_length=24)
    plans = models.ForeignKey('Plans')
    server = models.ForeignKey('Server')

    class Meta:
        unique_together = ('plans', 'server')


class AssetRecord(models.Model):
    """
    资产变更记录,orgid为空时，表示是资产汇报的数据。
    """
    orgid = models.CharField(u'所属ID', max_length=24, blank=True)
    asset = models.ForeignKey('Asset', verbose_name=u'资产对象')
    content = models.TextField(u'资产内容')
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = u"资产记录表"

    def __str__(self):
        return "%s-%s-%s[%s]" % (self.asset.rackunit.rack.idc.name,
                                 self.asset.rackunit.rack,
                                 self.asset.rackunit.unit_number,
                                 self.content)


class ErrorLog(models.Model):
    """
    错误日志,如：agent采集数据错误 或 运行错误
    """
    orgid = models.CharField(u'所属ID', max_length=24, null=True, blank=True)
    asset = models.ForeignKey('Asset', null=True, blank=True)
    title = models.CharField(u'标题', max_length=16)
    content = models.TextField(u'日志内容')
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = u"错误日志表"

    def __str__(self):
        return self.title


class CmdbLog(models.Model):
    level_choices = Choices('INFO', 'DEBUG', 'WARN', 'ERROR')
    level = StatusField('日志级别', choices_name='level_choices')
    orgid = models.CharField(u'所属ID', max_length=64)
    title = models.CharField(u'标题', max_length=64)
    content = models.TextField(u'内容')
    create_at = models.DateTimeField(u'创建时间')

    def __str__(self):
        return self.title
