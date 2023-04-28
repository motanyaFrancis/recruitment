import asyncio
import logging
import aiohttp
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.views import View
from myRequest.views import UserObjectMixins
from django.contrib import messages
from asgiref.sync import sync_to_async
import enum
from datetime import datetime

# Create your views here.
class Contact(UserObjectMixins,View):
    def get(self, request):
        try:
            ctx = {}
            response = {}
            username = 'None'
            ContactPage = True
            Dashboard = False
            Profile = False
            
            if 'authenticated' in request.session:
                authenticated = request.session['authenticated']
                username = request.session['E_Mail']
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
            'ContactPage':ContactPage,
            "email":username,
            "Dashboard":Dashboard,
            "Profile":Profile
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
            
            if 'authenticated' in request.session:
                authenticated = request.session['authenticated']
                
                if authenticated == True:
                    reply_email = request.session['E_Mail']
                    name = request.session['full_name']

            if ('authenticated' not in request.session and name == '') or ('authenticated' not in request.session and reply_email == ''):
                return JsonResponse({'success': False, 'error': 'email and name cannot be empty'})
            send_mail = self.send_message(name,reply_email,subject,
                                            message,email_template,recipient_email)
            if send_mail == True:
                return JsonResponse({'success': True, 'message': 'Your message has been sent. Thank you!'})
            return JsonResponse({'success': False, 'error': 'Not sent'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
class Profile(UserObjectMixins,View):
    async def get(self, request):
        try:
            ctx = {}
            response = {}
            username = 'None'
            ContactPage = False
            applicantNo = await sync_to_async(request.session.__getitem__)('No_')
            username = await sync_to_async (request.session.__getitem__)('full_name')
            email = await sync_to_async (request.session.__getitem__)('E_Mail')
            authenticated = await sync_to_async (request.session.__getitem__)('authenticated')
            Profile = True
            Dashboard = False
            personal_info = {}
            country = []
            tribes = []
            Study = []
            qualifications = []
            ctx = {}
            industry = []
            Bodies = []
            async with aiohttp.ClientSession() as session:
                personal_details = asyncio.ensure_future(self.simple_one_filtered_data(session,
                                                                                       '/QyApplicants',
                                                                                       "No_", 'eq',
                                                                                       applicantNo))
                get_country = asyncio.ensure_future(self.simple_fetch_data(session,
                                                                '/CountryRegion'))

                get_tribes = asyncio.ensure_future(self.simple_fetch_data(session,
                                                                    '/QyKenyanTribes'))
                field_of_study = asyncio.ensure_future(self.simple_fetch_data(session,
                                                                              '/QyFieldsOfStudy'))
                
                qualifications = asyncio.ensure_future(self.simple_fetch_data(session,
                                                                              '/QyQualificationCodes'))
                
                job_industries = asyncio.ensure_future(self.simple_fetch_data(session,
                                                                            '/QyJobIndustries'))
                
                pro_bodies = asyncio.ensure_future(self.simple_fetch_data(session,
                                                                          '/QyProfessionalBodies'))
                get_counties = asyncio.ensure_future(self.simple_fetch_data(session,
                                                                    '/QyCounties'))
                get_func_areas = asyncio.ensure_future(self.simple_fetch_data(session,
                                                                    '/QyFunctionalAreas'))
                pro_courses = asyncio.ensure_future(self.simple_fetch_data(session,
                                                                    '/QyProfessionalCourses'))
                
                response = await asyncio.gather(personal_details,get_country,
                                                get_tribes,field_of_study,qualifications,
                                                    job_industries,pro_bodies,get_counties,get_func_areas,pro_courses)
                
                for data in response[0]:
                    personal_info = data
                country =[country for country in response[1]]
                tribes = [tribe for tribe in response[2]]
                Study = [study for study in response[3]]
                qualifications = [qualification for qualification in response[4]]
                industry = [industry for industry in response[5]]
                Bodies = [body for body in response[6]]
                county = [county for county in response[7]]
                functional_areas = [areas for areas in response[8]]
                pro_course = [course for course in response[9]]
                
        except Exception as e:
            logging.exception(e)
            messages.error(request, f'{e}')
            return redirect('index')
        ctx = {
            'authenticated':authenticated,
            "response":response,
            'username':username,
            'ContactPage':ContactPage,
            "applicant": personal_info,
            "country": country,
            'tribes':tribes,
            'qualifications':qualifications,
            'Study':Study,
            'industry':industry,
            'pro_bodies':Bodies,
            'county':county,
            'functional_areas':functional_areas,
            "email":email,
            "Profile":Profile,
            "Dashboard":Dashboard,
            "pro_course":pro_course
        }
        return render(request,'profile.html',ctx)

class FnApplicantDetails(UserObjectMixins,View):
    def post(self,request):
        try:
            applicantNo = request.session['No_']
            disabilityGrade = 0
            firstName = request.POST.get('firstName')
            middleName = request.POST.get('middleName')
            lastName = request.POST.get('lastName')
            idNumber = request.POST.get('idNumber')
            genders = request.POST.get('gender')
            citizenship = request.POST.get('citizenship')
            countyCode = request.POST.get('countyCode')
            maritalStatus = int(request.POST.get('maritalStatus'))
            ethnicOrigin = request.POST.get('ethnicOrigin')
            disabled = int(request.POST.get('disabled'))
            dob = datetime.strptime((request.POST.get('dob')), '%Y-%m-%d').date()
            phoneNumber = request.POST.get('phoneNumber')
            postalAddress = request.POST.get('postalAddress')
            postalCode = request.POST.get('postalCode')
            residentialAddress = request.POST.get('residentialAddress')
            disabilityGrade = request.POST.get('disabilityGrade')
            if not countyCode:
                countyCode = ""
                
            if not disabilityGrade:
                disabilityGrade = 0
                
            if not ethnicOrigin:
                ethnicOrigin = ''
            class Data(enum.Enum):
                values = genders
            gender = (Data.values).value

            response = self.make_soap_request('FnApplicantDetails',
                                              applicantNo, firstName,
                                                middleName, lastName,
                                                    idNumber, gender,
                                                        citizenship,
                                                            countyCode, maritalStatus,
                                                                ethnicOrigin, disabled, dob,
                                                                    phoneNumber, postalAddress,
                                                                        postalCode, residentialAddress,
                                                                            int(disabilityGrade))
            if response == True:
                messages.success(request, "Successfully Added")
                return redirect('Profile')
        except Exception as e:
            messages.error(request, f'{e}')
            logging.exception(e)
            return redirect('Profile')
        
        
class AcademicQualifications(UserObjectMixins,View):
    def get(self,request):    
        try:
            Applicant_No_ = request.session['No_']
            qualifications = self.one_filter('/QyApplicantAcademicQualifications',
                                                'Applicant_No_',"eq",Applicant_No_)
           
            return JsonResponse(qualifications, safe=False)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, safe=False)

class QyApplicantJobExperience(UserObjectMixins,View):
    def get(self,request):    
        try:
            Applicant_No_ = request.session['No_']
            experience = self.one_filter('/QyApplicantJobExperience',
                                                'Applicant_No_',"eq",Applicant_No_)
            
            return JsonResponse(experience, safe=False)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, safe=False)
        
class QyApplicantJobProfessionalCourses(UserObjectMixins,View):
    def get(self,request):    
        try:
            Applicant_No_ = request.session['No_']
            pro_courses = self.one_filter('/QyApplicantJobProfessionalCourses',
                                                'Applicant_No_',"eq",Applicant_No_)
                        
            return JsonResponse(pro_courses, safe=False)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, safe=False)

class QyApplicantProfessionalMemberships(UserObjectMixins,View):
    def get(self,request):    
        try:
            Applicant_No_ = request.session['No_']
            pro_memberships = self.one_filter('/QyApplicantProfessionalMemberships',
                                                'Applicant_No_',"eq",Applicant_No_)
                        
            return JsonResponse(pro_memberships, safe=False)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, safe=False)
class QyApplicantHobbies(UserObjectMixins,View):
    def get(self,request):    
        try:
            Applicant_No_ = request.session['No_']
            hobbies = self.one_filter('/QyApplicantHobbies',
                                                'No_',"eq",Applicant_No_)
                        
            return JsonResponse(hobbies, safe=False)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, safe=False)
class QyApplicantReferees(UserObjectMixins,View):
    def get(self,request):    
        try:
            Applicant_No_ = request.session['No_']
            referees = self.one_filter('/QyApplicantReferees',
                                                'No',"eq",Applicant_No_)
                        
            return JsonResponse(referees, safe=False)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, safe=False)
class FnApplicantAcademicQualification(UserObjectMixins,View):
    def post(self,request):
        try:
            applicantNo = request.session['No_']
            lineNo = int(request.POST.get('lineNo'))
            myAction = request.POST.get('myAction')
            startDate = request.POST.get('startDate')
            endDate = request.POST.get('endDate')
            educationTypes = request.POST.get('educationType')
            educationLevels = request.POST.get('educationLevel')
            fieldOfStudy = request.POST.get('fieldOfStudy')
            qualificationCode = request.POST.get('qualificationCode')
            institutionName = request.POST.get('institutionName')
            proficiencyLevels = request.POST.get('proficiencyLevel')
            country = request.POST.get('country')
            isHighestLevel = request.POST.get('isHighestLevel')
            description = request.POST.get('description')
            grade = request.POST.get('grade')
            otherQualification = request.POST.get('otherQualification')

            class Data(enum.Enum):
                values = educationTypes
                education = educationLevels
                proficiency = proficiencyLevels

            educationType = (Data.values).value
            educationLevel = (Data.education).value
            proficiencyLevel = (Data.proficiency).value

            response = self.make_soap_request('FnApplicantAcademicQualification',
                                                applicantNo, lineNo, startDate,
                                                    endDate, educationType, educationLevel, 
                                                        fieldOfStudy, qualificationCode, institutionName,
                                                            proficiencyLevel, country, isHighestLevel,
                                                                description, grade, myAction, otherQualification)
            if response == True:
                return JsonResponse({'success': True, 'message': 'Successfully'})
            return JsonResponse({'success': False, 'message': f'{response}'})
        except Exception as e:
            error = "Upload failed: {}".format(e)
            logging.exception(e)
            return JsonResponse({'success': False, 'error': error})
        
class JobExperience(UserObjectMixins,View):
    def post(self,request):
        try:
            applicantNo = request.session['No_']
            lineNo = 0
            myAction = "insert"
            startDate  = datetime.strptime(request.POST.get('startDate'), '%Y-%m-%d').date()
            startDate = request.POST.get('startDate')
            endDate = request.POST.get('endDate')
            employer = request.POST.get('employer')
            industry = request.POST.get('industry')
            hierarchyLevels = request.POST.get('hierarchyLevel')
            functionalArea = request.POST.get('functionalArea')
            jobTitle = request.POST.get('jobTitle')
            isPresentEmployment = request.POST.get('isPresentEmployment')
            country = request.POST.get('country')
            description = request.POST.get('description')
            location = request.POST.get('location')
            employerEmail = request.POST.get('employerEmail')
            employerPostalAddress = request.POST.get('employerPostalAddress')
            lineNo = int(request.POST.get('lineNo'))
            myAction = request.POST.get('myAction')
            
            if not endDate:
                endDate = '0001-01-01'
                
            endDate = datetime.strptime(endDate, '%Y-%m-%d').date()

            class Data(enum.Enum):
                values = hierarchyLevels

            hierarchyLevel = (Data.values).value
            response = self.make_soap_request('FnApplicantJobExperience',
                                              applicantNo, lineNo, startDate,
                                                    endDate, employer, industry, hierarchyLevel, 
                                                    functionalArea, jobTitle,
                                                        isPresentEmployment, country, description,
                                                        location, employerEmail, 
                                                        employerPostalAddress,
                                                        myAction)
            if response == True:
                return JsonResponse({'success': True, 'message': 'Successfully'})
            return JsonResponse({'success': False, 'message': f'{response}'})
        except Exception as e:
            error = "Upload failed: {}".format(e)
            logging.exception(e)
            return JsonResponse({'success': False, 'error': error})
        
        
class FnApplicantProfessionalCourse(UserObjectMixins,View):
    def post(self,request):
        try:
            qualificationCode = request.POST.get('qualificationCode')
            sectionLevel = int(request.POST.get('sectionLevel'))
            otherQualification = request.POST.get('otherQualification')
            applicantNo = request.session['No_']
            lineNo = int(request.POST.get('lineNo'))
            myAction = request.POST.get('myAction')
            if not otherQualification:
                otherQualification = ''


            response = self.make_soap_request('FnApplicantProfessionalCourse',
                            applicantNo, lineNo, qualificationCode, sectionLevel,
                            myAction, otherQualification)
            if response == True:
                return JsonResponse({'success': True, 'message': 'Successfully'})
            return JsonResponse({'success': False, 'message': f'{response}'})
        except Exception as e:
            error = "Upload failed: {}".format(e)
            logging.exception(e)
            return JsonResponse({'success': False, 'error': error})
class FnApplicantProfessionalMembership(UserObjectMixins,View):
    def post(self,request):
        try:
            applicantNo = request.session['No_']
            lineNo = int(request.POST.get('lineNo'))
            myAction = request.POST.get('myAction')
            professionalBody = request.POST.get('professionalBody')
            membershipNo = request.POST.get('membershipNo')
            otherProfessionalBody = request.POST.get('otherProfessionalBody')
            
            if not otherProfessionalBody:
                otherProfessionalBody = ''

            response = self.make_soap_request('FnApplicantProfessionalMembership',
                                    applicantNo, lineNo, professionalBody, membershipNo,
                                    myAction, otherProfessionalBody)
            if response == True:
                return JsonResponse({'success': True, 'message': 'Successfully'})
            return JsonResponse({'success': False, 'message': f'{response}'})
        except Exception as e:
            error = "Upload failed: {}".format(e)
            logging.exception(e)
            return JsonResponse({'success': False, 'error': error})
class FnApplicantHobby(UserObjectMixins,View):
    def post(self,request):
        try:
            applicantNo = request.session['No_']
            lineNo = int(request.POST.get('lineNo'))
            myAction = request.POST.get('myAction')
            hobby = request.POST.get('hobby')

            response = self.make_soap_request('FnApplicantHobby',
                applicantNo, lineNo, hobby, myAction)

            if response == True:
                return JsonResponse({'success': True, 'message': 'Successfully'})
            return JsonResponse({'success': False, 'message': f'{response}'})
        except Exception as e:
            error = "Upload failed: {}".format(e)
            logging.exception(e)
            return JsonResponse({'success': False, 'error': error})
            
       
class FnApplicantReferee(UserObjectMixins,View):
    def post(self,request):
        try:
            applicantNo = request.session['No_']
            lineNo = int(request.POST.get('lineNo'))
            myAction = request.POST.get('myAction')
            names = request.POST.get('names')
            designation = request.POST.get('designation')
            company = request.POST.get('company')
            telephoneNo = request.POST.get('telephoneNo')
            email = request.POST.get('email')
            response = self.make_soap_request('FnApplicantReferee',
                            applicantNo, lineNo, names, designation,
                            company, telephoneNo, email, myAction)
            
            if response == True:
                return JsonResponse({'success': True, 'message': 'Successfully'})
            return JsonResponse({'success': False, 'message': f'{response}'})
        except Exception as e:
            error = "Upload failed: {}".format(e)
            logging.exception(e)
            return JsonResponse({'success': False, 'error': error})

