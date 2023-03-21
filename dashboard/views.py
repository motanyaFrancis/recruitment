import asyncio
import logging
import aiohttp
from django.shortcuts import render,redirect
from django.views import View
from myRequest.views import UserObjectMixins
from django.contrib import messages
from asgiref.sync import sync_to_async
from django.conf import settings as config
# Create your views here.
class Index(UserObjectMixins, View):
    def get(self, request):
        try:
            ctx = {}
            authenticated = False

            if 'authenticated' in request.session:
                authenticated = request.session['authenticated']
            else:
                authenticated = False
            
            response = self.double_filtered_data("/QyProcurementMethods","Status","eq",'New',
                        "and","TenderType","eq",'Open Tender')
            open_tenders = [x for x in response[1] if x['SubmittedToPortal'] == True]
        except Exception as e:
            logging.exception(e)
            messages.error(request, f'{e}')
            return redirect('index')
        print(authenticated)
        ctx = {"open_tenders":open_tenders,
               "authenticated":authenticated}
        return render(request,'index.html',ctx)
    
class TenderDetail(UserObjectMixins,View):
    def get(self, request,pk):
        try:
            ctx = {}
            response = {}
            if 'authenticated' in request.session:
                authenticated = request.session['authenticated']
            else:
                authenticated = False
            if 'Name' in request.session:
                username = request.session['Name']
            else:
                username = request.session['Email']
            task_get_procurement_methods = self.one_filter("/QyProcurementMethods","No","eq",pk)

            for x in task_get_procurement_methods[1]:
                response = x
        except Exception as e:
            logging.exception(e)
            messages.error(request, f'{e}')
            return redirect('index')
        ctx = {
            'authenticated':authenticated,
            "response":response,
            'username':username,
        }
        return render(request,'tenders/detail.html',ctx)


class Dashboard(UserObjectMixins,View):
    def get(self,request):
        try:
            ctx = {}
            state = 'Prospect'
            if 'authenticated' in request.session:
                authenticated = request.session['authenticated']
            else:
                authenticated = False
            if 'Name' in request.session:
                username = request.session['Name']
            else:
                username = request.session['Email']
            ProcURL = config.O_DATA.format("/QyProcurementMethods?$filter=SubmittedToPortal%20eq%20true")
            response = self.get_object(ProcURL)
            open_tenders = [x for x in response['value'] if x['TenderType'] == 'Open Tender' and x['Status'] == 'New']
            open_restricted = [x for x in response['value'] if x['TenderType'] == 'Restricted Tender' and x['Status'] == 'New']
            open_quotation = [x for x in response['value'] if x['Process_Type'] == 'RFQ' and x['Status'] == 'New']
            open_interest = [x for x in response['value'] if x['Process_Type'] == 'EOI' and x['Status'] == 'New']
            open_proposal = [x for x in response['value'] if x['Process_Type'] == 'RFP' and x['Status'] == 'New']
            total_open = len([x for x in response['value'] if x['Status'] == 'New'])
            total_closed = len([x for x in response['value'] if x['Status'] == 'Archived'])
            if 'UserId' in request.session:
                VendorNo = request.session['UserId']
                submitted = self.one_filter("/QyProspectiveSupplierTender","Vendor_No","eq",VendorNo)
                submitted_open = [x for x in submitted[1] if x['Type'] == 'Tender']
                submitted_restricted = [x for x in submitted[1] if x['Type'] == 'Restricted']
                submitted_quotation = [x for x in submitted[1] if x['Type'] == 'RFQ']
                submitted_interest = [x for x in submitted[1] if x['Type'] == 'EOI']
                submitted_proposal = [x for x in submitted[1] if x['Type'] == 'RFP']
                total_submitted = len([x for x in submitted[1]])
            if 'state' in request:
                state = request.session['state']
                
        except Exception as e:
            logging.exception(e)
            messages.error(request, f'{e}')
            return redirect('index')
        ctx = {
            'authenticated':authenticated,
            "open_tenders":open_tenders,
            'username':username,
            'open_restricted':open_restricted,
            'open_quotation':open_quotation,
            'open_interest':open_interest,
            'open_proposal':open_proposal,
            'submitted_open':submitted_open,
            'submitted_restricted':submitted_restricted,
            'submitted_quotation':submitted_quotation,
            'submitted_interest':submitted_interest,
            'submitted_proposal':submitted_proposal,
            'total_submitted':total_submitted,
            'total_open':total_open,
            'total_closed':total_closed,
            'state':state
        }
        return render(request,'dashboard.html',ctx)
def Logout(request):
    try:
        request.session.flush()
        messages.success(request,"Logged out successfully")
        return redirect('index')
    except Exception as e:
        print(e)
        return redirect('index')