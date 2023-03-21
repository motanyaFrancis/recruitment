import asyncio
import logging
import aiohttp
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.views import View
from myRequest.views import UserObjectMixins
from django.contrib import messages

# Create your views here.
class login_request(UserObjectMixins,View):
    def get(self, request):
        ctx = {}
        return render(request, 'login.html', ctx)
    def post(self,request):
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')

            vendors = self.one_filter("/QyVendorDetails","EMail","eq",email)

            for vendor in vendors[1]:
                if vendor['EMail'] == email:
                    if self.pass_decrypt(vendor['Password']) == password:
                        request.session['UserId'] = vendor['No']
                        request.session['state'] = "Vendor" 
                        request.session['authenticated'] = True  
                        request.session['Name'] = vendor['Name']
                        request.session['Email'] = vendor['EMail']
                        if password == 'Password@123': 
                            messages.success(request,f"Success. Logged in as {request.session['Name']}")
                            messages.info(request,'You are using a default password, reset it')                  
                            return redirect('dashboard')
                    messages.error(request, "Invalid Credentials. Please reset your password")
                    return redirect('index')
                    
            prospect = self.one_filter("/QyProspectiveSuppliers","Email","eq",email) 
                
            for prospect in prospect[1]:
                if prospect['Email'] == email:
                    if self.pass_decrypt(prospect['SerialID']) == password:
                        request.session['UserId'] = prospect['No']
                        request.session['state'] = "Prospect"
                        request.session['authenticated'] = True 
                        request.session['Email'] = prospect['Email']
                        messages.success(request,f"Success. Logged in as {request.session['Email']}")
                        return redirect('dashboard')
                    messages.error(request, "Invalid Credentials. Please reset your password else create a new account")
                    return redirect('index')
            messages.error(request, "User not Registered")
            return redirect('register')
        except Exception as e:
            messages.error(request, f"{e}")
            print(e)
            return redirect('index')
    
class Register(UserObjectMixins,View):
    async def get(self, request):
        try:
            ctx = {}
            async with aiohttp.ClientSession() as session:
                task_get_countries = asyncio.ensure_future(self.simple_fetch_data(session, '/QyCountryRegions'))
                response = await asyncio.gather(task_get_countries)
            ctx = {
                "countries":response[0]
            }
        except Exception as e:
            messages.error(request,f'{e}')
            logging.exception(e)
            return redirect('register')
        return render(request,'register.html',ctx)
    async def post(self, request):
        try:
            prospNo = request.POST.get('prospNo')
            supplierName = request.POST.get('supplierName')
            supplierMail = request.POST.get('supplierMail')
            countryRegionCode = request.POST.get('countryRegionCode')
            postalAddress = request.POST.get('postalAddress')
            postCode = request.POST.get('postCode')
            city = request.POST.get('city')
            contactPersonName = request.POST.get('contactPersonName')
            contactPhoneNo = request.POST.get('contactPhoneNo')
            contactMail = request.POST.get('contactMail')
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')
            myAction = request.POST.get('myAction')
            
            if not postalAddress:
                postalAddress = 'None'
                
            if not postCode:
                postCode = 'None'
            if not city:
                city = 'None'   
            if len(password) < 6:
                messages.error(request, 'Password should be at least 6 characters')
                return redirect('register')
            if password != password_confirm:
                messages.error(request, 'Password mismatch')
                return redirect('register')
            token = self.verificationToken(5)
            response = self.make_soap_request('FnProspectiveSupplierSignup',
                                              prospNo, supplierName, 
                                                    supplierMail, countryRegionCode,
                                                        postalAddress, postCode, city,contactPersonName,
                                                            contactPhoneNo, contactMail, self.pass_encrypt(password),
                                                                token, myAction)
            if response == True:
                email_subject = 'Activate your account'
                email_template = 'activate.html'
                recipient = supplierName
                recipient_email = supplierMail
                token = token
                send_verification_mail = self.send_mail(request,email_subject,
                                                        email_template,recipient,
                                                            recipient_email,token)
                if send_verification_mail == True:
                    messages.success(request, "We sent you an email to verify your account")
                    return redirect('verify')
                messages.error(request,'Verification Email not sent')
                return redirect('verify')
            messages.error(request, f'{response}')
            return redirect('register')
        except Exception as e:
            logging.exception(e)
            messages.error(request, f'{e}')
            return redirect('register')
        
class  verify_user(UserObjectMixins,View):
    def get(self, request):
        return render(request, 'verify.html')
    def post(self,request):
        try:
            email = request.POST.get('email')
            secret = request.POST.get('secret')
            verified = True
            prospect_users = self.one_filter("/QyProspectiveSuppliers",
                                    "Email","eq",email)
            for user in prospect_users[1]:
                if user['Verification_Token'] == secret:
                    response = self.make_soap_request('FnVerifiedProspectiveSupplier',
                                                      verified,email)
                    print(response)
                    if response == True:
                        return JsonResponse({'success': True, 'message': 'Verification Successful, login to continue'})
                    return JsonResponse({'success': False, 'error': 'Verification Failed'})
                return JsonResponse({'success': False, 'error': 'Wrong Secret Code'})
            return JsonResponse({'success': False, 'error': 'Wrong Email'})
        except  Exception as e:
            print(e)
            return JsonResponse({'success': False, 'error': str(e)})