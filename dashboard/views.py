import asyncio
import base64
import logging
import aiohttp
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from myRequest.views import UserObjectMixins
from django.contrib import messages
from asgiref.sync import sync_to_async
from django.conf import settings as config
from datetime import datetime
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

            open_vacancies = config.O_DATA.format("/QyRecruitmentRequests")
            response = self.get_object(open_vacancies)
            open_vacancy = [job for job in response['value']
                            if job['Status'] == 'Released' and job['Submitted_To_Portal'] == True
                            and datetime.strptime(job['End_Date'], '%Y-%m-%d') >= current_datetime
                            ]

        except Exception as e:
            logging.exception(e)
            messages.error(request, f'{e}')
            return redirect('index')

        ctx = {
            "open_vacancy": open_vacancy,
            "authenticated": authenticated,
            "ContactPage": ContactPage
        }
        return render(request, 'index.html', ctx)


class Detail(UserObjectMixins, View):
    def get(self, request, pk, no):
        try:
            ctx = {}
            response = {}
            username = 'None'
            userID = 'None'
            jobs = []
            Dashboard = False
            Profile = False
            ContactPage = False
            submitted_list = []

            if 'authenticated' in request.session:
                authenticated = request.session['authenticated']
                
                userID = request.session['No_']

                if 'Name' in request.session:
                    username = request.session['Name']
                else:
                    username = request.session['E_Mail']
                

                applied_jobs = self.one_filter(
                    "/QyApplicantJobApplied", "Application_No_", "eq", userID)
                submitted = [x for x in applied_jobs[1]]
                

                for jobs in applied_jobs[1]:
                    submitted_list.append(jobs['Job_ID'])
            else:
                authenticated = False

            RecruitmentRequests = self.one_filter(
                "/QyRecruitmentRequests", "Job_ID", "eq", pk)
            for x in RecruitmentRequests[1]:
                res = x
            AcademicQualifications = self.one_filter(
                "/QyJobAcademicQualifications", "Job_ID", "eq", pk)
            for Qualifications in AcademicQualifications[1]:
                if Qualifications['Job_ID'] == pk:
                    response = Qualifications
            qualify = [x for x in AcademicQualifications[1]]
            JobExperience = self.one_filter(
                '/QyJobExperienceQualifications', 'Job_ID', 'eq', pk)
            for Experience in JobExperience[1]:
                if Experience['Job_ID'] == pk:
                    E_response = Experience

            
            JobResponsibilities = self.one_filter(
                '/QyJobResponsibilities', 'Code', 'eq', pk)
            RESPOs = [x for x in JobResponsibilities[1]]
            JobKnowledgeSkills = self.one_filter(
                '/QyJobKnowledgeSkills', 'Code', 'eq', pk)
            Skill = [x for x in JobKnowledgeSkills[1]]
            ProfessionalCourses = self.one_filter(
                '/QyProfessionalCourses', 'Job_ID', 'eq', pk)
            Course = [x for x in ProfessionalCourses[1]]
            ProfessionalMemberships = self.one_filter(
                '/QyJobProfessionalMembeships', 'Job_ID', 'eq', pk)
            Member = [x for x in ProfessionalMemberships[1]]
            Supervising = self.one_filter(
                '/QyJobPositionsSupervising', 'Job_ID', 'eq', pk)
            Position = [x for x in Supervising[1]]

            # print(submitted)

        except Exception as e:
            logging.exception(e)
            messages.error(request, f'{e}')
            return redirect('index')
        ctx = {
            'authenticated': authenticated,
            "response": response,
            'username': username,
            "experience": E_response,
            "Qualifications": response,
            "res": res,
            "Skill": Skill,
            "RESPOs": RESPOs,
            "Course": Course,
            "JobMembeship": Member,
            "Position": Position,
            "email": username,
            "Dashboard": Dashboard,
            "Profile": Profile,
            "qualify": qualify,
            "ContactPage": ContactPage,
            'userID': userID,
            "submitted": jobs,
        }
        return render(request, 'detail.html', ctx)


class Dashboard(UserObjectMixins, View):
    def get(self, request):
        try:
            ctx = {}
            ContactPage = False
            current_datetime = datetime.now()
            username = request.session['full_name']
            email = request.session['E_Mail']
            Dashboard = True
            Profile = False
            submitted_list = []

            if 'authenticated' in request.session:
                authenticated = request.session['authenticated']
            else:
                authenticated = False

            applied_jobs = self.one_filter(
                "/QyApplicantJobApplied", "Application_No_", "eq", request.session['No_'])
            submitted = [x for x in applied_jobs[1]]

            for jobs in applied_jobs[1]:
                submitted_list.append(jobs['Job_ID'])

            ProcURL = config.O_DATA.format(
                "/QyRecruitmentRequests?$filter=Submitted_To_Portal%20eq%20true")
            response = self.get_object(ProcURL)
            open_vacancy = [job for job in response['value']
                            if job['Submitted_To_Portal'] == True and
                            datetime.strptime(job['End_Date'], '%Y-%m-%d') >= current_datetime and
                            job['Job_ID'] not in submitted_list]

        except Exception as e:
            logging.exception(e)
            messages.error(request, f'{e}')
            return redirect('index')
        ctx = {
            'authenticated': authenticated,
            'ContactPage': ContactPage,
            "open_vacancy": open_vacancy,
            'username': username,
            "email": email,
            "submitted": submitted,
            "Dashboard": Dashboard,
            "Profile": Profile
        }
        return render(request, 'dashboard.html', ctx)


def Logout(request):
    try:
        request.session.flush()
        messages.success(request, "Logged out successfully")
        return redirect('index')
    except Exception as e:
        print(e)
        return redirect('index')


class TechnicalRequirements(UserObjectMixins, View):
    async def get(self, request, pk, no):
        try:
            required_files = []
            async with aiohttp.ClientSession() as session:
                task_get_docs = asyncio.ensure_future(self.simple_one_filtered_data(session,
                                                                                    "/QyJobAttachments", "Job_ID", "eq", pk))
                task_get_attached = asyncio.ensure_future(self.simple_one_filtered_data(session,
                                                                                        '/QyDocumentAttachments', 'No_', 'eq', no))
                response = await asyncio.gather(task_get_docs, task_get_attached)

                attached = [x for x in response[1]]
                required_files = [x for x in response[0]]
                if attached:
                    required_files = required_files = [d for d in required_files if all(
                        d.get('Attachment') != a.get('File_Name') for a in attached)]
                else:
                    required_files = required_files
                return JsonResponse(required_files, safe=False)
        except Exception as e:
            logging.exception(e)
            return JsonResponse({'error': str(e)}, safe=False)


class Attachments(UserObjectMixins, View):
    async def get(self, request, no):
        try:
            applicantNo = await sync_to_async(request.session.__getitem__)('No_')
            Attachments = []
            async with aiohttp.ClientSession() as session:
                task_get_leave_attachments = asyncio.ensure_future(self.simple_one_filtered_data(session,
                                                                                                 "/QyDocumentAttachments", "No_", "eq", applicantNo))

                response = await asyncio.gather(task_get_leave_attachments)

                Attachments = [x for x in response[0]]
                # print(Attachments)
                return JsonResponse(Attachments, safe=False)
        except Exception as e:
            logging.exception(e)
            return JsonResponse({'error': str(e)}, safe=False)

    async def post(self, request, no):
        try:
            applicantNo = await sync_to_async(request.session.__getitem__)('No_')
            attachments = request.FILES.getlist('attachment')
            tableID = 52177607
            # fileName = no
            # response = False

            for file in attachments:
                fileName = request.FILES['attachments'].name
                attachment = base64.b64encode(file.read())

                response = self.make_soap_request('FnUploadAttachedDocument',
                                                  applicantNo, fileName, attachment,
                                                  tableID, applicantNo)
            if response is not None:
                if response == True:
                    message = "Uploaded {} attachments successfully".format(
                        len(attachments))
                    return JsonResponse({'success': True, 'message': message})
                error = "Upload failed: {}".format(response)
                return JsonResponse({'success': False, 'error': error})
            error = "Upload failed: Response from server was None"
            return JsonResponse({'success': False, 'error': error})
        except Exception as e:
            error = "Upload failed: {}".format(e)
            logging.exception(e)
            return JsonResponse({'success': False, 'error': error})
        
def fileUpload(request, pk, no):
    try:
        applicantNo = request.session['No_']
        attachments = request.FILES.getlist('attachments')
        tableID = 52177607
        

        for file in attachments:
                fileName = request.FILES['attachments'].name
                attachment = base64.b64encode(file.read())
                print('fileName:  ', fileName)

        # response = self.make_soap_request('FnUploadAttachedDocument',
        #                                           applicantNo, fileName, attachment,
        #                                           tableID, applicantNo)
        
        response = config.CLIENT.service.FnUploadAttachedDocument(
                       applicantNo, fileName, attachment, tableID, applicantNo
                        )
        if response is not None:
            if response == True:
                message = "Uploaded {} attachments successfully".format(
                    len(attachments))
                return redirect('Detail', pk=pk, no=no)
            error = "Upload failed: {}".format(response)
            return redirect('Detail', pk=pk, no=no)
        error = "Upload failed: Response from server was None"
        return redirect('Detail', pk=pk, no=no)
    except Exception as e:
        error = "Upload failed: {}".format(e)
        logging.exception(e)
        return redirect('Detail', pk=pk, no=no)

class DeleteAttachment(UserObjectMixins, View):
    def post(self, request):
        try:
            docID = int(request.POST.get('docID'))
            tableID = int(request.POST.get('tableID'))
            docNo = request.session['No_']
            print('docID: ', docID)
            print('tableID: ', tableID)
            print('docNo: ', docNo)
            response = self.make_soap_request("FnDeleteDocumentAttachment",
                                              docNo, docID, tableID)
            print('response: ', response)
            if response == True:
                return JsonResponse({'success': True, 'message': 'Deleted successfully'})
            return JsonResponse({'success': False, 'message': f'{response}'})
        except Exception as e:
            error = "Upload failed: {}".format(e)
            logging.exception(e)
            return JsonResponse({'success': False, 'error': error})


class Submit(UserObjectMixins, View):
    def post(self, request, no):
        try:
            applicantNo = request.session['No_']

            response = self.make_soap_request(
                'FnApplicantApplyJob', applicantNo, no)

            if response == True:
                return JsonResponse({'success': True, 'message': 'Submitted successfully'})
            return JsonResponse({'success': False, 'message': f'Not sent, try again'})
        except Exception as e:
            logging.exception(e)
            return JsonResponse({'success': False, 'error': f'{e}'})


class FnWithdrawJobApplication(UserObjectMixins, View):
    def post(self, request):
        try:
            applicantNo = request.session['No_']
            needCode = request.POST.get('needCode')

            response = self.make_soap_request('FnWithdrawJobApplication',
                                              applicantNo, needCode)

            if response == True:
                messages.success(request, "Application Cancelled successfully")
                return redirect('dashboard')
            messages.error(request, f"{response}")
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f"{e}")
            print(e)
            return redirect('dashboard')
