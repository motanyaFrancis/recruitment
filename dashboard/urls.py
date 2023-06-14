from django.urls import path
from . import views

urlpatterns = [
    path('', views.Index.as_view(),name='index'),
    path('details/<str:pk>/<str:no>', views.Detail.as_view(),name='Detail'),
    path('dashboard/', views.Dashboard.as_view(),name='dashboard'),
    path('logout/', views.Logout,name='logout'),
    path('TechnicalRequirements/<str:pk>/<str:no>/',views.TechnicalRequirements.as_view(),name='TechnicalRequirements'),
    path('Attachments/<str:no>/', views.Attachments.as_view(), name='Attachments'),
    path('DeleteAttachment/', views.DeleteAttachment.as_view(), name='DeleteAttachment'),
    path('Submit/<str:no>/',views.Submit.as_view(),name='Submit'),
    path('FnWithdrawJobApplication', views.FnWithdrawJobApplication.as_view(), name='FnWithdrawJobApplication'),
    # path('fileUpload/<str:pk>/<str:no>', views.fileUpload, name='fileUpload'),
]