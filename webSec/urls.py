from django.urls import path
from . import views

urlpatterns = [
<<<<<<< Updated upstream
    path('',views.signup_page,name='signup_page'),
    path('loginpage/',views.login_page, name='loginpage'),
    path('home/',views.land_page,name='home'),
    path('signup',views.User_Signup,name='signup'),
    path('login/',views.Login,name='login'),
=======
    path('',views.land_page),
   path('signup/', views.user_signup, name='signup'),
>>>>>>> Stashed changes
]