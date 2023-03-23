import logging
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.views import View
from myRequest.views import UserObjectMixins
from django.contrib import messages

# Create your views here.
class Contact(UserObjectMixins,View):
    def get(self, request):
        try:
            ctx = {}
            response = {}
            username = 'None'
            ContactPage = True
            if 'authenticated' in request.session:
                authenticated = request.session['authenticated']
                if 'Name' in request.session:
                    username = request.session['Name']
                else:
                    username = request.session['Email']
            else:
                authenticated = False
        except Exception as e:
            logging.exception(e)
            messages.error(request, f'{e}')
            return redirect('index')
        ctx = {
            'authenticated':authenticated,
            "response":response,
            'username':username,
            'ContactPage':ContactPage
        }
        return render(request,'contact.html',ctx)
    
class SendMessage(UserObjectMixins,View):
    def post(self, request):
        try:
            name = request.POST.get('name')
            reply_email = request.POST.get('email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            email_template = 'message.html'
            recipient_email = 'devops@kobby.co.ke'
            
            send_mail = self.send_message(name,reply_email,subject,
                                            message,email_template,recipient_email)
            if send_mail == True:
                return JsonResponse({'success': True, 'message': 'Your message has been sent. Thank you!'})
            return JsonResponse({'success': False, 'error': 'Not sent'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})