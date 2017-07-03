from django.shortcuts import render,HttpResponse
from django.views import View

class Index(View):

    def get(self,request):

        return HttpResponse('ok')
