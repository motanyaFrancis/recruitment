from django.urls import path
from . import views

urlpatterns = [
    path('', views.Index.as_view(),name='index'),
    path('tdr/<str:pk>/', views.TenderDetail.as_view(),name='TenderDetail'),
    path('dashboard/', views.Dashboard.as_view(),name='dashboard'),
    path('logout/', views.Logout,name='logout'),
]