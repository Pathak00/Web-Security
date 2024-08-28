from django.urls import path
from . import views

urlpatterns = [
    path('', views.land_page, name='land_page'),
   
]
