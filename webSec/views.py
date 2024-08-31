from django.shortcuts import render
from django.http import HttpResponse
from.models import *
# Create your views here.
def land_page(request):
    return render(request,'index.html')
def login_page(request):
    return render (request,'login.html')
def signup_page(request):
    return render (request,'signup.html')

# SignUp page View

def User_Signup(request):
    if request.method =='POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # User already exits oe not....

        user = Signup_user.objects.filter(Email = email)

        if user:
            message = "User Already Exist"
            return render(request,"signup.html",{'msg':message})
        
        else:
            if password1 == password2:
                newuser = Signup_user.objects.create(Username=username,Email=email,Password=password1,Conform_Password=password2)

                message = "User SignUp successfully"
                return render(request,"login.html",{'msg':message})
            else:
                message = "Password and conform password not matched..."
                return render(request,"signup.html",{'msg':message})
            
# Login Page View

def Login(request):
    if request.method =='POST':
        email = request.POST['email']
        password = request.POST['pass']

        user = Signup_user.objects.get(Email=email)

        if user:
            if user.Password == password:
                request.session['Username']=user.Username
                request.session['Email']=user.Email

                return render(request,"index.html")
            
            else:
                message = "Password not match"
                return render(request,"login.html",{'msg':message})
            
        else:
            message ="User does not exist"
            return render(request,"signup.html",{'msg':message})
    
