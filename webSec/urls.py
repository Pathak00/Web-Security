from django.urls import path,include
from . import views
from .views import dashboard
# from .views import get_user_reports


urlpatterns = [
    path('', views.land_page, name='land_page'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('register/',views.registerPage,name='register'),
    path('login/',views.login_view,name='login_view'),
    path('logout/', views.user_logout, name='user_logout'),
#    path('api/scan-reports/', views.fetch_scan_reports, name='fetch_scan_reports')
   
]
 


   


