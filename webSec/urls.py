from django.urls import path
from . import views
from .views import dashboard

urlpatterns = [
    path('', views.land_page, name='land_page'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('register/',views.registerPage,name='register'),
     path('login/',views.login_view,name='login_view'),


   
]



