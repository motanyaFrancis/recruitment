import asyncio
import logging
import aiohttp
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
        if request.method == 'POST':
            try:
                email = request.POST.get('email')
                password = request.POST.get('password')

                vendors = self.one_filter("/VendorDetails","EMail","eq",email)

                for vendor in vendors[1]:
                    if vendor['EMail'] == email:
                        if self.pass_decrypt(vendor['Password']) == password:
                            request.session['UserId'] = vendor['No']
                            request.session['state'] = "Vendor" 
                            request.session['authenticated'] = True  
                            if password == 'Password@123':
                                pass                        
                            return redirect('dashboard')
                        messages.error(request, "Invalid Credentials. Please reset your password else create a new account")
                        return redirect('login')
                        
                prospect = self.one_filter("/QyProspectiveSuppliers","Email","eq",email) 
                    
                for prospect in prospect[1]:
                    if prospect['Email'] == email and prospect['Verified'] == True:
                        print("Prospect")
                        if self.pass_decrypt(prospect['Password']) == password:
                            request.session['UserId'] = prospect['No']
                            request.session['state'] = "Prospect"
                            request.session['authenticated'] = True 
                            return redirect('dashboard')
                        messages.error(request, "Invalid Credentials. Please reset your password else create a new account")
                        return redirect('login')
                messages.error(request, "User not Registered")
                return redirect('login')
            except Exception as e:
                messages.error(request, f"{e}")
                print(e)
                return redirect('login')
        return redirect('login')
    
class Register(UserObjectMixins,View):
    async def get(self, request):
        async with aiohttp.ClientSession() as session:
            pass
            # task_get_countries = asyncio.ensure_future(self.simple_one_filtered_data(session, ))
            # response = await asyncio.gather(task_get_procurement_methods)
        return render(request,'register.html')
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
                    if response == True:
                        messages.success(request,"Verification Successful, login to continue")
                        return redirect('verify')
                    messages.error(request,"Verification Failed")
                    return redirect('verify')
                messages.error(request,"Wrong Secret Code")
                return redirect('verify')
            messages.error(request,"Wrong Email")
            return redirect('verify')
        except  Exception as e:
            print(e)
            messages.error(request,f"{e}")
            return redirect('verify')