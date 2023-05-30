import asyncio
import logging
import requests
import aiohttp
from django.conf import settings as config
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from myRequest.views import UserObjectMixins
from django.contrib import messages

# Create your views here.


class login_request(UserObjectMixins, View):
    def get(self, request):
        ctx = {}
        return render(request, 'index.html', ctx)

    def post(self, request):
        session = requests.Session()
        session.auth = config.AUTHS
        if request.method == 'POST':
            try:
                email = request.POST.get('email')
                password = request.POST.get('password')

                applicants = self.one_filter(
                    "/QyApplicants", "E_Mail", "eq", email)
                for applicant in applicants[1]:
                    
                    if applicant['E_Mail'] == email:
                        if applicant['Portal_Password'] != '':
                            if self.pass_decrypt(applicant['Portal_Password']) == password:
                                request.session['No_'] = applicant['No_']
                                print(request.session['No_'])
                                request.session['E_Mail'] = applicant["E_Mail"]
                                request.session['authenticated'] = True
                                request.session['full_name'] = applicant['First_Name'] + " " + applicant['Last_Name']
                                request.session.modified = True
                                messages.success(
                                    request, f"Success. Logged in as {request.session['full_name']}")
                                return redirect('dashboard')
                            
                            messages.error(request, "Password mismatch")
                            return redirect('index')
                        messages.error(
                            request, "Password not found. Please reset your password.")
                        return redirect('index')
            except Exception as e:
                messages.error(request, f"{e}")
                print(e)
                return redirect('index')
        return redirect('index')


class Register(UserObjectMixins, View):
    async def get(self, request):
        return render(request, 'register.html')

    async def post(self, request):
        try:
            email = request.POST.get('email')
            my_password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            agree = request.POST.get('agree')
            dataPrivacy = False
            if agree == 'on':
                dataPrivacy = True

            if len(my_password) < 6:
                messages.error(
                    request, 'Password should be at least 6 characters')
                return redirect('register')
            if my_password != confirm_password:
                messages.error(request, 'Password mismatch')
                return redirect('register')
            if dataPrivacy == True:
                token = self.verificationToken(5)
                response = self.make_soap_request('FnApplicantRegister',
                                                  email, self.pass_encrypt(my_password), dataPrivacy, token)
                if response == True:
                    email_subject = 'Activate your account'
                    email_template = 'activate.html'
                    recipient = email
                    recipient_email = email
                    token = token
                    send_verification_mail = self.send_mail(request, email_subject,
                                                            email_template, recipient,
                                                            recipient_email, token)
                if send_verification_mail == True:
                    messages.success(
                        request, "We sent you an email to verify your account")
                    return redirect('verify')
                messages.error(request, 'Verification Email not sent')
                return redirect('verify')
            messages.error(request, f'{response}')
            return redirect('register')
        except Exception as e:
            logging.exception(e)
            messages.error(request, f'{e}')
            return redirect('register')


class FnResetEmail(UserObjectMixins, View):
    def post(self, request):
        if request.method == 'POST':
            try:
                emailAddress = request.POST.get('emailAddress')
                vendors = self.one_filter(
                    "/QyVendorDetails", "EMail", "eq", emailAddress)
                for vendor in vendors[1]:
                    if vendor['EMail'] == emailAddress:
                        email_subject = 'Password Reset'
                        email_template = 'resetMail.html'
                        recipient = vendor['Name']
                        recipient_email = vendor['EMail']
                        token = self.verificationToken(5)
                        reset_data = {
                            "user": "Vendor",
                            "Email": vendor['EMail'],
                            "token": token
                        }
                        request.session['resetMail'] = reset_data
                        send_rest_mail = self.send_mail(request, email_subject, email_template,
                                                        recipient, recipient_email, token)
                        if send_rest_mail == True:
                            messages.success(
                                request, "We sent you an email to reset your password")
                            return redirect('FnResetPassword')
                        messages.error(request, 'Reset failed contact admin')
                        return redirect('FnResetPassword')
                prospects = self.one_filter(
                    "/QyProspectiveSuppliers", "Email", "eq", emailAddress)
                for prospect in prospects[1]:
                    if prospect['Email'] == emailAddress and prospect['Verified'] == True:
                        email_subject = 'Password Reset'
                        email_template = 'resetMail.html'
                        recipient = prospect['ContactPersonName']
                        recipient_email = prospect['Email']
                        token = self.verificationToken(5)
                        reset_data = {
                            "user": "Prospect",
                            "Email": prospect['Email'],
                            "token": token
                        }
                        request.session['resetMail'] = reset_data
                        send_reset_mail = self.send_mail(request, email_subject, email_template,
                                                         recipient, recipient_email, token)
                        if send_reset_mail == True:
                            messages.success(
                                request, 'We sent you an email to reset your password')
                            return redirect('FnResetPassword')
                        messages.error(request, 'Reset failed contact admin')
                        return redirect('FnResetPassword')
                    messages.error(request, 'Reset failed, email not verified')
                    return redirect('index')
            except Exception as e:
                print(e)
                messages.error(request, f'{e}')
        return redirect('index')


class FnResetPassword(UserObjectMixins, View):
    def get(self, request):
        return render(request, 'reset.html')

    def post(self, request):
        try:
            reset_data = request.session['resetMail']
            verificationToken = request.POST.get('verificationToken')
            password = request.POST.get('password')
            password2 = request.POST.get('password2')

            if verificationToken != reset_data['token']:
                messages.error(request, "Incorrect Verification Token")
                return redirect('FnResetPassword')
            if len(password) < 6:
                messages.error(
                    request, "Password should be at least 6 characters")
                return redirect('FnResetPassword')
            if password != password2:
                messages.error(request, "Password mismatch")
                return redirect('FnResetPassword')

            response = self.make_soap_request('FnResetPassword',
                                              reset_data['Email'], self.pass_encrypt(password), verificationToken)
            if response == True:
                del request.session['resetMail']
                messages.success(
                    request, "Reset successful, login to continue")
                return redirect('index')
            messages.success(request, f"{response}")
            return redirect('index')
        except Exception as e:
            messages.error(request, f"{e}")
            print(e)
            return redirect('FnResetPassword')


class verify_user(UserObjectMixins, View):
    def get(self, request):
        return render(request, 'verify.html')

    def post(self, request):
        try:
            email = request.POST.get('email')
            secret = request.POST.get('secret')
            verified = True
            prospect_users = self.one_filter("/QyApplicants",
                                             "E_Mail", "eq", email)
            for user in prospect_users[1]:
                if user['Verification_Token'] == secret:
                    response = self.make_soap_request('FnVerifyEmailAddress',
                                                      email, verified)
                    if response == True:
                        return JsonResponse({'success': True, 'message': 'Verification Successful, login to continue'})
                    return JsonResponse({'success': False, 'error': 'Verification Failed'})
                return JsonResponse({'success': False, 'error': 'Wrong Secret Code'})
            return JsonResponse({'success': False, 'error': 'Wrong Email'})
        except Exception as e:
            print(e)
            return JsonResponse({'success': False, 'error': str(e)})
