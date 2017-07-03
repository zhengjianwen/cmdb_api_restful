from rest_framework.response import Response
from cmdb.settings import CONTENT_TYPE


def processdata(ret, request=None, *args, **kwargs):
    rformat = request.query_params.get('format')
    if str(rformat).lower() == 'json':
        return Response(ret, content_type=CONTENT_TYPE)
    else:
        return Response(ret)
