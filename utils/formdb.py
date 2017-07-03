#!/usr/bin/env python
# -*- coding=utf-8 -*-

from django.forms import Form
from django.forms import fields
from django.core.validators import RegexValidator
from django.forms import widgets
from django.core.exceptions import ValidationError
from asset.models import *
from idc.models import *
from rack.models import *
import re


class AssetForm(Form):
    sn = fields.CharField(max_length=64, required=True,)
    hostname = fields.CharField(max_length=128)
    orgid = fields.CharField(validators=[RegexValidator(r'^[0-9]+$', 'Have to number')])
    vendor = fields.CharField(max_length=32)
    disk = fields.CharField(max_length=32, required=True)
    mem = fields.CharField(max_length=32, required=True)
    cpu = fields.CharField(max_length=32, required=True)
    raid = fields.CharField()
    product_name = fields.CharField(max_length=64)
    plans = fields.CharField(max_length=32, required=True)
    owner = fields.CharField(max_length=64, required=True)
    tags = fields.CharField(max_length=64, required=True)
    idc = fields.CharField(max_length=32, required=True)
    rack = fields.CharField(max_length=64, required=True)
    int_ip = fields.GenericIPAddressField(max_length=64, required=True)
    ext_ip = fields.GenericIPAddressField(max_length=64, required=True)
    ilo_ip = fields.GenericIPAddressField(max_length=64, required=True)
    os = fields.CharField(max_length=32, required=True)
    mac = fields.CharField(max_length=64,required=True)
    create_at = fields.CharField(max_length=8,
                                 validators=[RegexValidator(r'^\d+$','Have to number')])
    rack_unit = fields.IntegerField()
    note = fields.CharField(max_length=128)
    status = fields.CharField()

    def clean_rack_unit(self):
        value = self.cleaned_data.get('rack_unit',None)
        if value:
            value = int(value)
            if value > 0 and value < 13:
                return value
        elif not value:
            return value
        else:
            raise ValidationError('The rack unit is not correct')

    def clean_rack(self):
        value = self.cleaned_data.get('rack', None)
        if not value:
            return value
        elif value and Rack.objects.filter(name=value).count():
            return value
        else:
            raise ValidationError('Not has this rack')

    def clean_plans(self):
        value = self.cleaned_data.get('plans')
        if value and Plans.objects.filter(name=value).count():
            return value
        elif not value:
            return value
        else:
            raise ValidationError('There is no such data')

    def clean_vendor(self):
        value = self.cleaned_data.get('vendor')
        ret = Vendor.objects.filter(name=value)
        if not ret:
            raise ValidationError('vendor not find','invalid')
        return value

    def clean_raid(self):
        value = self.cleaned_data.get('raid')
        raid_choices = ('RAID5', 'RAID0', 'RAID1', 'RAID10', 'RAID6', 'DIRECT')
        if value not in raid_choices:
            raise ValidationError('Raid choices is error', 'invalid')
        return value

    def clean_status(self):
        value = self.cleaned_data.get('status',None)

        status_choices = ('RUNNING', 'MAINTANCING', 'STOCK')
        if str(value).upper() not in status_choices:
            raise ValidationError('status is error')
        return value

    def clean_idc(self):
        value = self.cleaned_data['idc']
        if not value:
            return value
        elif value and IDC.objects.filter(name=value).count():
            return value
        else:
            raise ValidationError('Invalid IDC name')

    def clean_create_at(self):
        value = self.cleaned_data.get('create_at', None)
        value = value.replace('-','')
        value = value.replace('/','')
        if re.match(r'^20[01]{1}\d{1}[01]{1}\d{01}',value):
            value = value[:6]
        elif re.match(r'^19\d{2}[01]{1}\d{1}$',value):
            value = value[:6]
        elif not value:
            return value
        else:
           raise ValidationError('datetime is error', 'invalid')

        return value

    def clean_mac(self):
        value = self.cleaned_data['mac']
        mac = re.match(r'\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2}', value)
        if value and mac:
            return mac.group()
        if not value:
            return value
        else:
            raise ValidationError('mac is format error', 'invalid')


    def clean(self):
        sn = self.cleaned_data.get('sn')
        orgid = self.cleaned_data.get('orgid')
        ret = Asset.objects.filter(sn=sn, orgid=orgid)
        if ret:
            raise ValidationError('Data is duplicated','invalid')
        return self.cleaned_data