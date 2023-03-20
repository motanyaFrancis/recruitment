import asyncio
import logging
import aiohttp
from django.shortcuts import render,redirect
from django.views import View
from myRequest.views import UserObjectMixins
from django.contrib import messages

# Create your views here.
class Index(UserObjectMixins,View):
    async def get(self, request):
        try:
            ctx = {}
            if 'authenticated' not in request.session:
                authenticated = False
            else:
                authenticated = request.session['authenticated']
            async with aiohttp.ClientSession() as session:
                task_get_procurement_methods = asyncio.ensure_future(self.simple_double_filtered_data(session,
                                                                                            '/QyProcurementMethods',
                                                                                                'Status','eq','New','and',
                                                                                                    'TenderType','eq','Open Tender'))
                response = await asyncio.gather(task_get_procurement_methods)
                open_tenders = [x for x in response[0] if x['SubmittedToPortal'] == True]
        except Exception as e:
            logging.exception(e)
            messages.error(request, f'{e}')
            return redirect('index')
        print(authenticated)
        ctx = {"open_tenders":open_tenders,
               "authenticated":authenticated}
        return render(request,'index.html',ctx)
class TenderDetail(UserObjectMixins,View):
    async def get(self, request,pk):
        try:
            ctx = {}
            response = {}
            if 'authenticated' not in request.session:
                authenticated = False
            else:
                authenticated = request.session['authenticated']
            async with aiohttp.ClientSession() as session:
                task_get_procurement_methods = asyncio.ensure_future(self.simple_one_filtered_data(session,
                                                                                            '/QyProcurementMethods',
                                                                                                'No','eq',pk))
                response = await asyncio.gather(task_get_procurement_methods)
                for x in response[0]:
                    response = x
        except Exception as e:
            logging.exception(e)
            messages.error(request, f'{e}')
            return redirect('index')
        ctx = {
            'authenticated':authenticated,
            "response":response,
        }
        return render(request,'tenders/detail.html',ctx)

class Dashboard(UserObjectMixins,View):
    def get(self,request):
        return render(request,'dashboard.html')
