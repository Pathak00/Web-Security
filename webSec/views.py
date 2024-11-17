# myapp/views.py

from django.shortcuts import render
from django.http import HttpResponse
from .crawler import DomainFetcher
from urllib.parse import urlparse
import socket
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm  
from .forms import CreateUserForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from .headers import scan_website_headers
from io import BytesIO
from reportlab.pdfgen import canvas
import os
from reportlab.lib.pagesizes import letter
from django.conf import settings


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
                    
             
                headers_output=scan_website_headers(domain_url)
                pdf_response = generate_pdf(domain_url, headers_output)
                return pdf_response
                # return HttpResponse(f'Crawling result:<br>{result_html}')

    return render(request, 'index.html')
            


def generate_pdf(domain_url, headers):
    # Create a BytesIO buffer to hold the PDF data
    buffer = BytesIO()

    # Create a PDF canvas object
    c = canvas.Canvas(buffer, pagesize=letter)

    # Set up the PDF document title and font
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, 750, "WebSecurity: Website Scan Results")

    # Optionally, add a logo at the top-left corner (make sure to update the path to your logo file)
    logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'images', 'logo.png')  
    try:
        c.drawImage(logo_path, 50, 730, width=100, height=50)
    except:
        print("Logo not found, proceeding without logo")

    # Add the domain URL and "Important Headers" heading
    c.setFont("Helvetica", 12)
    c.drawString(100, 710, f"Website Scan Results for: {domain_url}")
    c.drawString(100, 690, "Important Headers:")

    # Draw a border around the content area
    c.setStrokeColorRGB(0, 0, 0)  # Black color for border
    c.setLineWidth(1)
    c.rect(50, 100, 500, 600)  # Rectangle with x, y, width, and height (from bottom-left corner)

    # Loop through headers and write them to the PDF, adjusting the position for each line
    y_position = 650
    for header, value in headers.items():
        if y_position < 120:  # Prevent content from going off the page
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = 750
        c.drawString(100, y_position, f"{header}: {value}")
        y_position -= 20

    # Finalize the PDF page and save it
    c.showPage()
    c.save()

    # Move the buffer position to the beginning of the PDF
    buffer.seek(0)

    # Create an HTTP response that sends the PDF as a downloadable file
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="website_scan_results.pdf"'

    return response



   
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
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')
        else:
           for field in form:
                for error in field.errors:
                    messages.error(request, error)

            
    context={'form':form}
    return render(request,'register.html',context)


def user_logout(request):
    logout(request)
    return redirect('login_view')