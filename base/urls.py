from django.urls import path
from . import views

urlpatterns = [
    path('Contact/', views.Contact.as_view(),name='Contact'),
    path('SendMessage/', views.SendMessage.as_view(), name='SendMessage'),
    path('Profile/', views.Profile.as_view(), name='Profile'),
]