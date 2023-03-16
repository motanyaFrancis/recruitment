from django.shortcuts import render
from django.views import View
from myRequest.views import UserObjectMixins

# Create your views here.
class Index(UserObjectMixins,View):
    def get(self, request):
        return render(request,'index.html')