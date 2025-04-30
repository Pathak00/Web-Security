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
from .headers import check_website_headers
from io import BytesIO
from reportlab.pdfgen import canvas
import os
from reportlab.lib.pagesizes import letter
from django.conf import settings
from .scanner import get_javascript_libraries, check_vulnerabilities
from django.http import JsonResponse, HttpResponse
from reportlab.lib.pagesizes import A4
import subprocess
from bs4 import BeautifulSoup
from flask import Flask, Response
from django.shortcuts import redirect
import json
from .models import VulnerabilityScanReport
from django.contrib.auth.decorators import login_required


def land_page(request):
    if request.method == 'POST':
        if 'name' in request.POST:
            domain_url = request.POST.get('name')
            if not domain_url.startswith("http://") and not domain_url.startswith("https://"):
                domain_url = "https://" + domain_url

            fetcher = DomainFetcher(domain_url)
            if domain_url:
                # if fetcher.is_valid_domain(domain_url):
                #     results = fetcher.crawl_domain()
                #     result_html = '<br>'.join(results)
                # else:
                #     result_html = 'Invalid URL'
                result_html=''
                # Detect JavaScript libraries using scanner.py
                libraries = get_javascript_libraries(domain_url)
               
                vulnerabilities = check_vulnerabilities(libraries)
                
                # Format vulnerabilities into an HTML string for display
                vulnerabilities_html = ""
                for vuln in vulnerabilities:
                    # vulnerabilities_html += f"<p><b>Library:</b> {vuln['library']}</p>"
                    for issue in vuln['vulnerabilities']:
                        vulnerabilities_html += f"<p>- CVE: {issue['CVE']}, Description: {issue['description']}</p>"
                        
                # Append vulnerabilities to result_html
                result_html += f"<br><h3>Vulnerable JavaScript Libraries:</h3>{vulnerabilities_html}"

                # Run SQLMap on the domain
                sqlmap_output, sqlmap_error, databases = run_sqlmap(domain_url, parameters={'dbs': None, 'threads': '4'})

                # Add SQLMap output and database names to result_html
                result_html += f"<br><h3>SQLMap Results:</h3><pre>{sqlmap_output}</pre>"
                if sqlmap_error:
                    result_html += f"<br><h3>SQLMap Errors:</h3><pre>{sqlmap_error}</pre>"

                # Include database names in a formatted manner
                if databases:
                    # result_html += "<br><h3>Available Databases:</h3><ul>"
                    for db in databases:
                        result_html += f"<li>{db}</li>"
                    result_html += "</ul>"

                # Scan website headers
                headers_output = scan_website_headers(domain_url)
                
                severity=check_website_headers(domain_url)
                
                pdf_response = generate_pdf(domain_url, headers_output, vulnerabilities, result_html)
             
                if request.user.is_authenticated:
                # If the user is authenticated, return the PDF inline
                    # response = HttpResponse(pdf_response, content_type='application/pdf')
                    # response['Content-Disposition'] = 'inline; filename="report.pdf"'
                    context = {
                        'username': request.user.username,
                        'pdf_response': json.dumps(pdf_response),
                         'severity':json.dumps(severity)                # Passing the raw dictionary to the template
                        }
                     
                    report = VulnerabilityScanReport(
                    username=context['username'],
                    pdf_response=json.loads(context['pdf_response']),
                    domain=domain_url,# Convert JSON string back to dictionary
                    severity=json.loads(context['severity'])  # Convert JSON string back to dictionary
                    )
                    report.save()
                    
                    return render(request,'dashboard.html',context)
                    # return response
                else:
                # If the user is not logged in, redirect them to the login page for download
                    messages.warning(request, "You need to log in to access the result.")
                    return redirect('login_view')

                # # Generate PDF including vulnerable libraries and SQLMap results
                # pdf_response = generate_pdf(domain_url, headers_output, vulnerabilities, result_html)
                # response = HttpResponse(pdf_response, content_type='application/pdf')
                # response['Content-Disposition'] = 'inline; filename="report.pdf"'
                # return pdf_response

    return render(request, 'index.html')

def generate_pdf(domain_url, headers_output, vulnerabilities, result_html):
    
    report_data = {}

    # Add domain URL and headers output to the report data
    report_data['domain_url'] = domain_url
    report_data['headers_output'] = headers_output

    # Add vulnerabilities to the report data
    report_data['vulnerabilities'] = vulnerabilities

    # Process the HTML (result_html) to extract the list of databases
    if result_html:
        soup = BeautifulSoup(result_html, 'html.parser')
        databases = [li.get_text(strip=True) for li in soup.find_all('li')]
        report_data['databases'] = databases
    else:
        report_data['databases'] = []
    
    report_json = json.dumps(report_data, indent=4)
    
   
    return report_data
    
    # If not authenticated, redirect to the login page
  
   
def dashboard(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return render(request, 'dashboard.html',{'username': request.user.username}) 
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



def run_sqlmap(url, parameters=None, timeout=300):
    # Base sqlmap command
    sqlmap_command = [
        'python',
        r'C:\Users\rupak\OneDrive\Desktop\crypto\sqlmap-master\sqlmap.py',
        '-u', 
        url,
        '--batch',  # Run in non-interactive mode (skip prompts)
        '--output-dir=output',  # Save output to 'output' folder
        '--random-agent',  # Use a random User-Agent to mimic different browsers
        '--level=1',  # Increase test level for more thorough testing
        '--risk=1',
        '--thread=3'# Maximum risk for more tests
    ]
    
    # Add any user-provided parameters (such as --dbs, --tables, etc.)
    if parameters:
        for key, value in parameters.items():
            sqlmap_command.append(f"--{key}")
            if value:
                sqlmap_command.append(value)

    try:
        # Execute the sqlmap command with a timeout
        process = subprocess.Popen(sqlmap_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(timeout=timeout)

        # Return results as strings
        output = stdout.decode() if stdout else ""
        error_output = stderr.decode() if stderr else ""
        
        # Extract relevant details (databases in this case)
        databases = []
        for line in output.splitlines():
            if line.startswith("[*]") and not line.startswith("[*] starting") and not line.startswith("[*] ending"):
                databases.append(line.strip())
               
        
        # Return both the output and the list of databases
        return output, error_output, databases

    except subprocess.TimeoutExpired:
        return None, f"Error: The command timed out after {timeout} seconds.", []
    except KeyboardInterrupt:
        return None, "Execution was interrupted by the user.", []
    except Exception as e:
        return None, f"Error running sqlmap: {e}", []
    

# def user_scan_reports(request):
#     # Fetch the scan reports for the logged-in user
#     user_reports = VulnerabilityScanReport.objects.filter(username=request.user.username)

#     # Prepare the reports to be passed to the template
#     reports_data = []
#     for report in user_reports:
#         vulnerabilities = report.get_pdf_response().get('vulnerabilities', [])
#         severity = report.get_severity()

#         reports_data.append({
#             'domain': report.domain,
#             'severity': severity,
#             'vulnerabilities': vulnerabilities,
#             'created_at': report.created_at,
#             'pdf_response': report.get_pdf_response(),  # You may want to return this to display PDF as well
#         })

#     return render(request, 'dashboard.html', {
#         'reports_data': reports_data,
#         'username': request.user.username,
#     })
    
# def vulnerability_reports(request):
#     # Fetch reports for the logged-in user
#     user_reports = VulnerabilityScanReport.objects.filter(username=request.user.username)

#     print("user_reports")
#     print(user_reports)
#     # Prepare the data to pass to the template
#     reports_data = []
#     for report in user_reports:
#         pdf_response = report.get_pdf_response()
#         severity = report.get_severity()
        
#         reports_data.append({
#             'domain': report.domain,
#             'pdf_response': pdf_response,  # Parsed JSON object for PDF response
#             'severity': severity,  # Parsed JSON object for severity
#             'created_at': report.created_at.strftime('%B %d, %Y'),  # Date format
#         })

#     # Render the template with the reports data
#     return render(request, 'dashboard.html', {
#         'username': request.user.username,
#         'reports_data': reports_data,  # Passing data to the frontend
#     })
    


# def fetch_scan_reports(request):
#     reports = VulnerabilityScanReport.objects.all()
#     data = []
#     print(reports)
#     for report in reports:
#         try:
#             pdf_response = json.loads(report.pdf_response) if report.pdf_response else {}
#             severity = json.loads(report.severity) if report.severity else {}
#         except json.JSONDecodeError:
#             pdf_response = {"error": "Invalid JSON in pdf_response"}
#             severity = {"error": "Invalid JSON in severity"}

#         data.append({
#             "id": report.id,
#             "username": report.username,
#             "domain_url": report.domain,
#             "pdf_response": pdf_response,
#             "severity": severity,
#             "created_at": report.created_at.strftime("%Y-%m-%d %H:%M:%S"),
#         })

#     return JsonResponse(data, safe=False)