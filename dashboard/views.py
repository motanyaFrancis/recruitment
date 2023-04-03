import asyncio
import base64
import logging
import aiohttp
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.views import View
from myRequest.views import UserObjectMixins
from django.contrib import messages
from asgiref.sync import sync_to_async
from django.conf import settings as config
from datetime import datetime
import io as BytesIO
import base64
from django.http import HttpResponse

# Create your views here.
class Index(UserObjectMixins, View):
    def get(self, request):
        try:
            ctx = {}
            authenticated = False
            ContactPage = False
            current_datetime = datetime.now()  

            if 'authenticated' in request.session:
                authenticated = request.session['authenticated']
            else:
                authenticated = False
            
            response = self.double_filtered_data("/QyProcurementMethods","Status","eq",'New',
                        "and","TenderType","eq",'Open Tender')
            open_tenders = [x for x in response[1] 
                                if x['SubmittedToPortal'] == True and
                                    datetime.strptime(x['Release_Date'] + 
                                    ' ' + x['Release_Time'],'%Y-%m-%d %H:%M:%S') <= current_datetime
                                    and datetime.strptime(x['Quotation_Deadline'] + ' ' 
                                + x['Expected_Closing_Time'],'%Y-%m-%d %H:%M:%S') >= current_datetime]
        except Exception as e:
            logging.exception(e)
            messages.error(request, f'{e}')
            return redirect('index')

        ctx = {"open_tenders":open_tenders,
               "authenticated":authenticated,
               "ContactPage":ContactPage}
        return render(request,'index.html',ctx)
    
class TenderDetail(UserObjectMixins,View):
    def get(self, request,pk):
        try:
            ctx = {}
            response = {}
            username = 'None'
            current_datetime = datetime.now()  
            applicable = False
            if 'authenticated' in request.session:
                authenticated = request.session['authenticated']
                if 'Name' in request.session:
                    username = request.session['Name']
                else:
                    username = request.session['Email']
            else:
                authenticated = False
            
            task_get_procurement_methods = self.one_filter("/QyProcurementMethods","No","eq",pk)
            
            res_file = self.one_filter("/QyDocumentAttachments","No_","eq",pk)
            allFiles = [x for x in res_file[1]]
            
            for x in task_get_procurement_methods[1]:
                response = x
                if authenticated == True and datetime.strptime(x['Quotation_Deadline'] + ' ' + x['Expected_Closing_Time'],'%Y-%m-%d %H:%M:%S') >= current_datetime:
                    applicable = True
                                  
            procurement_lines = self.one_filter('/QyProcurementMethodLines','RequisitionNo','eq',pk)
            lines = [x for x in procurement_lines[1]]

        except Exception as e:
            logging.exception(e)
            messages.error(request, f'{e}')
            return redirect('index')
        ctx = {
            'authenticated':authenticated,
            "response":response,
            'username':username,
            'lines':lines,
            'applicable':applicable,
            "file":allFiles
        }
        return render(request,'tenders/detail.html',ctx)


class Dashboard(UserObjectMixins,View):
    def get(self,request):
        try:
            ctx = {}
            state = 'Prospect'
            ContactPage = False
            current_datetime = datetime.now()  
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
            open_tenders = [x for x in response['value'] if x['TenderType'] == 'Open Tender'
                            and x['Status'] == 'New' and datetime.strptime(x['Quotation_Deadline'] 
                                + ' ' + x['Expected_Closing_Time'],'%Y-%m-%d %H:%M:%S') >= current_datetime
                            and datetime.strptime(x['Release_Date'] + 
                                    ' ' + x['Release_Time'],'%Y-%m-%d %H:%M:%S') <= current_datetime]
            open_restricted = [x for x in response['value'] if x['TenderType'] == 'Restricted Tender'
                               and x['Status'] == 'New' and datetime.strptime(x['Quotation_Deadline'] + 
                                    ' ' + x['Expected_Closing_Time'],'%Y-%m-%d %H:%M:%S') >= current_datetime
                               and datetime.strptime(x['Release_Date'] + 
                                    ' ' + x['Release_Time'],'%Y-%m-%d %H:%M:%S') <= current_datetime]
            open_quotation = [x for x in response['value'] if x['Process_Type'] == 'RFQ' and x['Status'] == 'New' 
                              and datetime.strptime(x['Quotation_Deadline'] + ' ' 
                                + x['Expected_Closing_Time'],'%Y-%m-%d %H:%M:%S') >= current_datetime
                              and datetime.strptime(x['Release_Date'] + 
                                    ' ' + x['Release_Time'],'%Y-%m-%d %H:%M:%S') <= current_datetime]
            open_interest = [x for x in response['value'] if x['Process_Type'] == 'EOI' and x['Status'] == 'New' 
                            and datetime.strptime(x['Quotation_Deadline'] + ' ' 
                                                  + x['Expected_Closing_Time'],'%Y-%m-%d %H:%M:%S') >= current_datetime
                            and datetime.strptime(x['Release_Date'] + 
                                    ' ' + x['Release_Time'],'%Y-%m-%d %H:%M:%S') <= current_datetime]
            open_proposal = [x for x in response['value'] if x['Process_Type'] == 'RFP' 
                             and x['Status'] == 'New' and datetime.strptime(x['Quotation_Deadline'] +
                                ' ' + x['Expected_Closing_Time'],'%Y-%m-%d %H:%M:%S') >= current_datetime
                             and datetime.strptime(x['Release_Date'] + 
                                    ' ' + x['Release_Time'],'%Y-%m-%d %H:%M:%S') <= current_datetime]
            total_open = len([x for x in response['value'] if x['Status'] == 'New' 
                              and datetime.strptime(x['Quotation_Deadline'] + ' ' + 
                                 x['Expected_Closing_Time'],'%Y-%m-%d %H:%M:%S') >= current_datetime
                              and datetime.strptime(x['Release_Date'] + 
                                    ' ' + x['Release_Time'],'%Y-%m-%d %H:%M:%S') <= current_datetime])
            total_closed = len([x for x in response['value'] if x['Status'] == 'Archived'])
            
            all_tenders = [x for x in response['value'] if x['Status'] == 'New' 
                           and datetime.strptime(x['Quotation_Deadline'] + ' ' 
                                                 + x['Expected_Closing_Time'],'%Y-%m-%d %H:%M:%S') >= current_datetime
                           and datetime.strptime(x['Release_Date'] + 
                                    ' ' + x['Release_Time'],'%Y-%m-%d %H:%M:%S') <= current_datetime]
            
            
            if 'UserId' in request.session:
                VendorNo = request.session['UserId']
                submitted = self.one_filter("/QyProspectiveSupplierTender","Vendor_No","eq",VendorNo)
                all_submitted = [x for x in submitted[1]]
                submitted_open = [x for x in submitted[1] if x['Type'] == 'Tender']
                submitted_restricted = [x for x in submitted[1] if x['Type'] == 'Restricted']
                submitted_quotation = [x for x in submitted[1] if x['Type'] == 'RFQ']
                submitted_interest = [x for x in submitted[1] if x['Type'] == 'EOI']
                submitted_proposal = [x for x in submitted[1] if x['Type'] == 'RFP']
                total_submitted = len([x for x in submitted[1]])
            if 'state' in request.session:
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
            'state':state,
            'ContactPage':ContactPage,
            'all_tenders':all_tenders,
            'all_submitted':all_submitted
        }
        return render(request,'dashboard.html',ctx)
    
class FnCreateProspectiveSupplier(UserObjectMixins,View):
    def get(self,request):
        try:
            response = {}
            tenderNo = request.GET.get('tenderNo')
            user_id = request.session['UserId']
            task_get_procurement_methods = self.double_filtered_data("/QyProspectiveSupplierTender",
                                    "Tender_No_","eq",tenderNo,'and','Vendor_No','eq',user_id)
            
            for x in task_get_procurement_methods[1]:
                response = x
                return JsonResponse({'success': True,'response':response}, safe=False)
            return JsonResponse({'success': False,'response':str(0)}, safe=False)
        except Exception as e:
            logging.exception(e)
            return JsonResponse({'error': str(e)}, safe=False)
        
    def post(self,request):
        try:
            if 'UserId' in request.session:
                vendNo = request.session['UserId']
                Process_Type = request.POST.get('Process_Type')
                TenderType = request.POST.get('TenderType')
                docNo = request.POST.get('docNo')
                securityInstitution = request.POST.get('securityInstitution')
                securityAmount = request.POST.get('securityAmount')
                myAction = request.POST.get('myAction')
                
                if Process_Type == 'Tender' and TenderType== 'Open Tender':
                    procurementMethod = 1
                elif Process_Type == 'Tender' and TenderType== "Restricted Tender":
                    procurementMethod = 5
                elif Process_Type == 'RFQ':
                    procurementMethod = 2
                elif Process_Type== 'EOI':
                    procurementMethod = 4
                elif Process_Type == 'RFP':
                    procurementMethod = 3
                    
                if 'state' in request.session:
                    if request.session['state'] == 'Vendor':
                        userType = 'vendor'
                    elif request.session['state'] == 'Prospect':
                        userType = 'prospective'
                         
                response = self.make_soap_request('FnSupplierResponseHeader',vendNo,
                                                        procurementMethod,docNo,userType,
                                                            securityInstitution,float(securityAmount),myAction)
                if response != 'None' and response !='': 
                    return JsonResponse({'success': True, 'message': str(response)})
                return JsonResponse({'success': False, 'error': str(response)})
            return JsonResponse({'success': False, 'error': 'Session Expired. Please Login Again'})
        except Exception as e:
            logging.exception(e)
            return JsonResponse({'success': False, 'error': str(e)})
class Listing(UserObjectMixins,View):
    def get(self,request,type):
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
            open_tenders = [x for x in response['value'] if x['TenderType'] == type and x['Status'] == 'New']

            total_open = len([x for x in response['value'] if x['Status'] == 'New'])

            if 'UserId' in request.session:
                VendorNo = request.session['UserId']
                submitted = self.one_filter("/QyProspectiveSupplierTender","Vendor_No","eq",VendorNo)
                submitted_open = [x for x in submitted[1] if x['Type'] == 'Tender']
                submitted_restricted = [x for x in submitted[1] if x['Type'] == 'Restricted']
                submitted_quotation = [x for x in submitted[1] if x['Type'] == 'RFQ']
                submitted_interest = [x for x in submitted[1] if x['Type'] == 'EOI']
                submitted_proposal = [x for x in submitted[1] if x['Type'] == 'RFP']
                total_submitted = len([x for x in submitted[1]])
            if 'state' in request.session:
                state = request.session['state']
                
        except Exception as e:
            logging.exception(e)
            messages.error(request, f'{e}')
            return redirect('index')
        ctx = {
            'authenticated':authenticated,
            "open_tenders":open_tenders,
            'username':username,
            'submitted_open':submitted_open,
            'submitted_restricted':submitted_restricted,
            'submitted_quotation':submitted_quotation,
            'submitted_interest':submitted_interest,
            'submitted_proposal':submitted_proposal,
            'total_submitted':total_submitted,
            'total_open':total_open,
            'state':state,'type':type
        }
        return render(request,'tenders/list.html',ctx)                 
def Logout(request):
    try:
        request.session.flush()
        messages.success(request,"Logged out successfully")
        return redirect('index')
    except Exception as e:
        print(e)
        return redirect('index')
class TechnicalRequirements(UserObjectMixins,View):
    async def get(self,request,pk):
        try:
            required_files = []       
            async with aiohttp.ClientSession() as session:
                task_get_docs = asyncio.ensure_future(self.simple_one_filtered_data(session,
                                         "/QyProcurementRequiredDocuments","QuoteNo","eq",pk))
                task_get_attached = asyncio.ensure_future(self.simple_one_filtered_data(session,
                                                                '/QyDocumentAttachments','No_','eq',pk))
                response = await asyncio.gather(task_get_docs,task_get_attached)
    
                attached = [x for x in response[1]]  
                required_files = [x for x in response[0]]
                if attached:
                    required_files = [d for d in required_files if all(d.get('DocumentCode') != a.get('File_Name') for a in attached)]
                else:
                    required_files = required_files
                return JsonResponse(required_files, safe=False)

        except Exception as e:
            logging.exception(e)
            return JsonResponse({'error': str(e)}, safe=False)
class Attachments(UserObjectMixins,View):
    async def get(self,request,pk):
        try:
            Attachments = []         
            async with aiohttp.ClientSession() as session:
                task_get_leave_attachments = asyncio.ensure_future(self.simple_one_filtered_data(session,
                                         "/QyDocumentAttachments","No_","eq",pk))

                response = await asyncio.gather(task_get_leave_attachments)

                Attachments = [x for x in response[0]]
                return JsonResponse(Attachments, safe=False)
        except Exception as e:
            logging.exception(e)
            return JsonResponse({'error': str(e)}, safe=False)
    async def post(self, request, pk):
        try:
            userID = await sync_to_async(request.session.__getitem__)('UserId')
            attachments = request.FILES.getlist('attachment')
            tableID =52177788 
            fileName = request.POST.get("attachmentCode")
            response = False
            for file in attachments:
                attachment = base64.b64encode(file.read())
                response = self.upload_attachment(pk, fileName, attachment,
                                                tableID, userID)
            if response is not None:
                if response == True:
                    message = "Uploaded {} attachments successfully".format(len(attachments))
                    return JsonResponse({'success': True, 'message': message})
                error = "Upload failed: {}".format(response)
                return JsonResponse({'success': False, 'error': error})
            error = "Upload failed: Response from server was None"
            return JsonResponse({'success': False, 'error': error})
        except Exception as e:
            error = "Upload failed: {}".format(e)
            logging.exception(e)
            return JsonResponse({'success': False, 'error': error})
class DeleteAttachment(UserObjectMixins,View):
    def post(self,request):
        try:
            docID = int(request.POST.get('docID'))
            tableID= int(request.POST.get('tableID'))
            leaveCode = request.POST.get('leaveCode')
            response = self.delete_attachment(leaveCode,docID,tableID)
            if response == True:
                return JsonResponse({'success': True, 'message': 'Deleted successfully'})
            return JsonResponse({'success': False, 'message': f'{response}'})
        except Exception as e:
            error = "Upload failed: {}".format(e)
            logging.exception(e)
            return JsonResponse({'success': False, 'error': error})

class FinancialBid(UserObjectMixins,View):
    def get(self,request,pk):
        try:
            response = {}
            if 'UserId' in request.session:
                user_id = request.session['UserId']
                state = request.session['state']
                if state == 'Vendor':
                    task_get_procurement_methods = self.double_filtered_data("/QySupplierTenderLines","Tender_No_","eq",pk, 
                                                                'and', 'Vendor_No_', 'eq', user_id)
                elif state == 'Prospect':
                    task_get_procurement_methods = self.double_filtered_data("/QySupplierTenderLines","Tender_No_","eq",pk,
                                                                'and', 'Response_No', 'eq', user_id)
                response = [x for x in task_get_procurement_methods[1]]
                return JsonResponse(response, safe=False)
        except Exception as e:
            logging.exception(e)
            return JsonResponse({'error': str(e)}, safe=False)
    def post(self, request,pk):
        try:
            vendorNo = request.POST.get('Vendor_No_')
            prospectNo = request.POST.get('prospectNo')
            docNo = pk
            lineNo = request.POST.get('lineNo')
            unitPrice = request.POST.get('unitPrice')
            
            response = self.make_soap_request('FnSupplierResponseLine',
                                              prospectNo,docNo,vendorNo,lineNo,unitPrice)  
            
            if response == True:          
                return JsonResponse({'success': True, 'message': 'added successfully'})
            return JsonResponse({'success': False, 'error': f'{response}'})
        except Exception as e:
            logging.exception(e)
            return JsonResponse({'error': str(e)}, safe=False)  
    
class Submit(UserObjectMixins,View):
    def post(self,request,pk):
        try:
            prospectNo = request.session['UserId']
            Process_Type = request.POST.get('Process_Type')
            TenderType = request.POST.get('TenderType')
            
            if Process_Type == 'Tender' and TenderType== 'Open Tender':
                procurementMethod = 1
            elif Process_Type == 'Tender' and TenderType== "Restricted Tender":
                procurementMethod = 5
            elif Process_Type == 'RFQ':
                procurementMethod = 2
            elif Process_Type== 'EOI':
                procurementMethod = 4
            elif Process_Type == 'RFP':
                procurementMethod = 3
            
            docID = pk
            response = self.make_soap_request('FnSupplierSubmitResponse',prospectNo,
                                            procurementMethod,docID)
            print(response)
            if response == True:
                return JsonResponse({'success': True, 'message': 'Submitted successfully'})
            return JsonResponse({'success': False, 'message': f'Not sent, try again'})
        except Exception as e:
            logging.exception(e)
            return JsonResponse({'success': False, 'error': f'{e}'})
        
        
        
class viewDocs(UserObjectMixins,View):
    def post(self,request,pk,id):
        docNo = pk
        attachmentID = int(request.POST.get('attachmentID'))
        File_Name = request.POST.get('File_Name')
        File_Extension = request.POST.get('File_Extension')
        tableID = int(id)

        try:
            response = self.download_attachment(docNo, attachmentID, tableID)
            file_name = File_Name.split()
            filenameFromApp = file_name[0] + "." + File_Extension
            buffer = BytesIO.BytesIO()
            content = base64.b64decode(response)
            buffer.write(content)
            responses = HttpResponse(
                buffer.getvalue(),
                content_type="application/ms-excel",
            )
            responses['Content-Disposition'] = f'inline;filename={filenameFromApp}'
            return responses
        except Exception as e:
            messages.info(request, f'{e}')
            return redirect('index')