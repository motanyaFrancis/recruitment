from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.Register.as_view(),name='register'),
    path('verify/', views.verify_user.as_view(),name='verify'),
    path('login/', views.login_request.as_view(),name='login'),
    path('FnResetPassword/', views.FnResetPassword.as_view(),name='FnResetPassword'),
    path('FnResetEmail/', views.FnResetEmail.as_view(),name='FnResetEmail'),
]