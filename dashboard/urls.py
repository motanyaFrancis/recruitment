from django.urls import path
from . import views

urlpatterns = [
    path('', views.Index.as_view(),name='index'),
    path('tdr/<str:pk>/', views.TenderDetail.as_view(),name='TenderDetail'),
    path('procurement/<str:type>/', views.Listing.as_view(),name='procurement'),
    path('dashboard/', views.Dashboard.as_view(),name='dashboard'),
    path('logout/', views.Logout,name='logout'),
    path('FnCreateProspectiveSupplier/',views.FnCreateProspectiveSupplier.as_view(),name='FnCreateProspectiveSupplier'),
    path('TechnicalRequirements/<str:pk>/',views.TechnicalRequirements.as_view(),name='TechnicalRequirements'),
    path('Attachments/<str:pk>/', views.Attachments.as_view(), name='Attachments'),
    path('DeleteAttachment/', views.DeleteAttachment.as_view(), name='DeleteAttachment'),
    path('FinancialBid/<str:pk>/',views.FinancialBid.as_view(),name='FinancialBid'),
    path('Submit/<str:pk>/',views.Submit.as_view(),name='Submit'),
    path('getDocs/<str:pk>/<str:id>/', views.viewDocs.as_view(), name='getDocs'),
]