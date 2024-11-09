# myapp/views.py

from django.shortcuts import render
from django.http import HttpResponse
from .crawler import DomainFetcher
from urllib.parse import urlparse
import socket
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm  
from .forms import CreateUserForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login





def land_page(request):
    if request.method == 'POST':
        if 'name' in request.POST:
            domain_url = request.POST.get('name')
            if not domain_url.startswith("http://") and not domain_url.startswith("https://"):
                domain_url = "https://" + domain_url
            fetcher=DomainFetcher(domain_url)
            if domain_url:
                if fetcher.is_valid_domain(domain_url):
                    results = fetcher.crawl_domain()
                    result_html = '<br>'.join(results)
                else:
                    result_html = 'Invalid URL'
                return HttpResponse(f'Crawling result:<br>{result_html}')
    return render(request, 'index.html')
            
   
def dashboard(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return render(request, 'dashboard.html') 
        else:
            print("Error Invalid")
            return render(request, 'index.html', {'error': 'Invalid credentials'})

    return render(request, 'index.html')
        
        
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Authenticate and log the user in
            user = form.get_user()
            auth_login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'register.html', {'form': form, 'error': 'Please correct the errors below.'})
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})
    
def registerPage(request):
    form=CreateUserForm()
    
    if request.method=='POST':
        form=CreateUserForm(request.POST)
        print(form.errors)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')
        else:
           for field in form:
                for error in field.errors:
                    messages.error(request, error)

            
    context={'form':form}
    return render(request,'register.html',context)