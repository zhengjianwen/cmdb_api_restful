from django.contrib import admin
from repository import models


class LiasionAdmin(admin.ModelAdmin):
    list_display = ['orgid','name','phone','position','work_content']


class VendorAdmin(admin.ModelAdmin):
    list_display = ['orgid','name','address']


class IdcAdmin(admin.ModelAdmin):
    list_display = ['orgid', 'name', 'description', 'address']


class RackAdmin(admin.ModelAdmin):
    list_display = ['orgid','name','idc','room','max_units','power_capacity']


class AssetAdmin(admin.ModelAdmin):
    list_display = ['id','orgid','device_type','device_status','vendor','product_name','manage_ip','unit','create_at']


admin.site.register(models.IDC, IdcAdmin)
admin.site.register(models.Liasion, LiasionAdmin)
admin.site.register(models.Vendor, VendorAdmin)
admin.site.register(models.Rack, RackAdmin)
admin.site.register(models.RackUnit)
admin.site.register(models.IPSection)
admin.site.register(models.Asset,AssetAdmin)
admin.site.register(models.Server)
admin.site.register(models.NetworkDevice)
admin.site.register(models.Cpu)
admin.site.register(models.Memory)
admin.site.register(models.NIC)
admin.site.register(models.Disk)
admin.site.register(models.Plans)
admin.site.register(models.AssetRecord)
admin.site.register(models.ErrorLog)
admin.site.register(models.Tags)
