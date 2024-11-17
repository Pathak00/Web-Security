from django.urls import path,include
from . import views
from .views import dashboard

urlpatterns = [
    path('', views.land_page, name='land_page'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('register/',views.registerPage,name='register'),
    path('login/',views.login_view,name='login_view'),
    path('logout/', views.user_logout, name='user_logout'),
    #  path('', include('webSec.urls')),


   
]



