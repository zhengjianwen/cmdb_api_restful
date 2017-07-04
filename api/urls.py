from django.conf.urls import url, include
from rest_framework import routers, authtoken
from rest_framework.authtoken import views as authtoken_views
from api.views import restview,asset
from utils import fileviews
from api.views import asset

router = routers.DefaultRouter()
router.register(r'liasion/(?P<orgid>\d+)', restview.LiaisonViewSet)
router.register(r'vendor/(?P<orgid>\d+)', restview.VendorViewSet)
router.register(r'idc/(?P<orgid>\d+)', restview.IDCViewSet)
router.register(r'rack/(?P<orgid>\d+)', restview.RackViewSet)
router.register(r'rackunit/(?P<orgid>\d+)', restview.RackUnitViewSet)
router.register(r'ipsection/(?P<orgid>\d+)', restview.IPSectionViewSet)
router.register(r'tags/(?P<orgid>\d+)', restview.TagsViewSet)
router.register(r'cpu/(?P<orgid>\d+)', restview.CPUViewSet)
router.register(r'disk/(?P<orgid>\d+)', restview.DiskViewSet)
router.register(r'nic/(?P<orgid>\d+)', restview.NICViewSet)
router.register(r'memory/(?P<orgid>\d+)', restview.MemoryViewSet)
router.register(r'plans/(?P<orgid>\d+)', restview.PlansViewSet)
router.register(r'planserver/(?P<orgid>\d+)', restview.PSViewSet)
router.register(r'asset/(?P<orgid>\d+)', asset.AssetViewSet)
router.register(r'server/(?P<orgid>\d+)', asset.ServerViewSet)
router.register(r'network/(?P<orgid>\d+)', asset.NetworkDeviceViewSet)



# 自定义url接口
urlpatterns = [
    url(r'^upload/(?P<orgid>\d+)/', fileviews.AssetUploadViewSet.as_view()),
    url(r'^down/(?P<orgid>\d+)/', fileviews.AssetDownViewSet.as_view()),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    #url(r'^api-token-auth/', authtoken_views.obtain_auth_token)
]
