from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.Register.as_view(),name='register'),
    path('verify/', views.verify_user.as_view(),name='verify'),
]