from django.urls import path
from . import views

urlpatterns = [
    path('Contact/', views.Contact.as_view(),name='Contact'),
    path('SendMessage/', views.SendMessage.as_view(), name='SendMessage'),
    path('Profile/', views.Profile.as_view(), name='Profile'),
    path('FnApplicantDetails', views.FnApplicantDetails.as_view(), name="FnApplicantDetails"),
    path('AcademicQualifications', views.AcademicQualifications.as_view(), name="AcademicQualifications"),
    path('QyApplicantJobExperience', views.QyApplicantJobExperience.as_view(), name="QyApplicantJobExperience"),
    path('QyApplicantJobProfessionalCourses', views.QyApplicantJobProfessionalCourses.as_view(), name="QyApplicantJobProfessionalCourses"),
    path('QyApplicantProfessionalMemberships',views.QyApplicantProfessionalMemberships.as_view(),name='QyApplicantProfessionalMemberships'),
    path('QyApplicantHobbies', views.QyApplicantHobbies.as_view(), name='QyApplicantHobbies'),
    path('QyApplicantReferees', views.QyApplicantReferees.as_view(), name='QyApplicantReferees'),
    path('FnApplicantAcademicQualification', views.FnApplicantAcademicQualification.as_view(), name='FnApplicantAcademicQualification'),
    path('JobExperience', views.JobExperience.as_view(), name="JobExperience"),
    path('FnApplicantProfessionalCourse', views.FnApplicantProfessionalCourse.as_view(),name="FnApplicantProfessionalCourse"),
    path('FnApplicantProfessionalMembership', views.FnApplicantProfessionalMembership.as_view(),name='FnApplicantProfessionalMembership'),
    path('FnApplicantHobby', views.FnApplicantHobby.as_view(), name='FnApplicantHobby'),
    path('FnApplicantReferee', views.FnApplicantReferee.as_view(), name='FnApplicantReferee'),
]