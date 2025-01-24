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
from django.utils.timezone import now
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


def land_page(request):
    if request.method == 'POST':
        if 'name' in request.POST:
            
            domain_url = request.POST.get('name')
            print("domain_url",domain_url)
            if not domain_url.startswith("http://") and not domain_url.startswith("https://"):
                domain_url = "https://" + domain_url

            # fetcher = DomainFetcher(domain_url)
            if domain_url:
           
                # if fetcher.is_valid_domain(domain_url):
                #     results = fetcher.crawl_domain()
                #     result_html = '<br>'.join(results)
                # else:
                #     result_html = 'Invalid URL'
                result_html=[]
                
                # Detect JavaScript libraries using scanner.py
                libraries = get_javascript_libraries(domain_url)
                
                vulnerabilities = check_vulnerabilities(libraries)
                
                # Format vulnerabilities into an HTML string for display
                vulnerabilities_html = ""
                for vuln in vulnerabilities:
                    # Add library name (optional, can uncomment if needed)
                    vulnerabilities_html += f"<p><b>Library:</b> {vuln['library']}</p>"

                    # Loop through each issue (vulnerability) of the library
                    for issue in vuln['vulnerabilities']:
                        vulnerabilities_html += f"<p>- CVE: {issue['CVE']}, Description: {issue['description']}</p>"

                # Add the HTML string to result_html (assuming result_html is defined elsewhere)
                result_html = f"<br><h3>Vulnerable JavaScript Libraries:</h3>{vulnerabilities_html}"

    

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
               
           
                pdf_response = generate_pdf(headers_output, vulnerabilities, result_html,severity)
         
                if request.user.is_authenticated:
                # If the user is authenticated, return the PDF inline
                    # response = HttpResponse(pdf_response, content_type='application/pdf')
                    # response['Content-Disposition'] = 'inline; filename="report.pdf"'
                    
                    if VulnerabilityScanReport.objects.filter(domain=domain_url,username=request.user.username).exists():
                        context = {
                            'error_message': "A report for this domain already exists."
                        }
                        return render(request, 'dashboard.html', context)
    
                    context = {
                        'success_message': "Report saved successfully.",
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


def generate_pdf(headers_output, vulnerabilities, result_html,severity):
    # Initialize the report data dictionary
    report_data = {}

    # Add headers output to the report data
    report_data['headers_output'] = format_headers(headers_output)

    # Add vulnerabilities to the report data
    report_data['vulnerabilities'] = format_vulnerabilities(vulnerabilities)

    # Extract and add databases from the HTML content
    report_data['databases'] = extract_databases(result_html)
    
    report_data['severity'] = severity

    print("severity",report_data)
    return report_data
    
    # If not authenticated, redirect to the login page
def format_headers(headers_output):
    """Format headers into a neat dictionary."""
    formatted_headers = {}
    for header, value in headers_output.items():
        formatted_headers[header] = value if value else 'Not present'
    return formatted_headers


def format_vulnerabilities(vulnerabilities):
    """Format vulnerabilities into a readable list."""
    formatted_vulnerabilities = []
    for vulnerability in vulnerabilities:
        formatted_vulnerabilities.append({
            'library': vulnerability.get('library', 'Unknown'),
            'vulnerabilities': vulnerability.get('vulnerabilities', [])
        })
    return formatted_vulnerabilities


def extract_databases(result_html):
    """Extract list of databases from the HTML if present."""
    if result_html:
        soup = BeautifulSoup(result_html, 'html.parser')
        databases = [li.get_text(strip=True) for li in soup.find_all('li')]
        return databases
    else:
        return [] 
   
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
        found_database=False
        for line in output.splitlines():
            if line.startswith("[*]") and not line.startswith("[*] starting") and not line.startswith("[*] ending"):
                databases.append(line.strip())
                found_database=True
            
        if not found_database:
            databases.append("No any Databases Found")
               
        
        # Return both the output and the list of databases
        print("Database",databases)
        return output, error_output, databases

    except subprocess.TimeoutExpired:
        return None, f"Error: The command timed out after {timeout} seconds.", []
    except KeyboardInterrupt:
        return None, "Execution was interrupted by the user.", []
    except Exception as e:
        return None, f"Error running sqlmap: {e}", []
 
def fetch_scan_reports(request):
        reports = VulnerabilityScanReport.objects.filter(username=request.user.username)
        data = []
        print("report")
        print(reports)
        for report in reports:
            try:
                # Safely parse the JSON fields
                pdf_response = json.loads(report.pdf_response) if report.pdf_response else {}
                severity = json.loads(report.severity) if report.severity else {}
            except json.JSONDecodeError as e:
                # Handle JSON parsing errors
                pdf_response = {"error": f"Invalid JSON in pdf_response: {str(e)}"}
                severity = {"error": f"Invalid JSON in severity: {str(e)}"}

            # Ensure the data is in dictionary format
            if not isinstance(pdf_response, dict):
                pdf_response = {"error": "Unexpected format in pdf_response"}
            if not isinstance(severity, dict):
                severity = {"error": "Unexpected format in severity"}
            
            data.append({
                "id": report.id,
                "username": report.username,
                "domain_url": report.domain,
                "pdf_response": report.pdf_response,
                "severity": report.severity,
                "created_at": report.created_at.strftime("%Y-%m-%d"),
            })

        return JsonResponse(data, safe=False)
   
@csrf_exempt
@require_POST
def delete_vulnerability_scan_report(request):
    try:
        # Parse the incoming JSON data
        data = json.loads(request.body)

        # Get domain_url from the parsed data
        domain_url = data.get('domain_url')
        print(domain_url)
        # Check if domain_url is provided
        if not domain_url:
            return JsonResponse({"error": "Domain URL is required."}, status=400)

        # Try to find the report and delete it
        report = VulnerabilityScanReport.objects.get(domain=domain_url,username=request.user.username)
        report.delete()

        return JsonResponse({"message": "Report deleted successfully."}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)
    except VulnerabilityScanReport.DoesNotExist:
        return JsonResponse({"error": "Report not found."}, status=404)
    
def analyze_headers_and_vulnerabilities(result):
    headers_output = result.get('headers_output', {})
    vulnerabilities = result.get('vulnerabilities', [])
    databases = result.get('databases', [])
    
    # Initialize analysis results
    analysis = {
        'header_issues': [],
        'vulnerability_issues': [],
        'database_issues': []
    }

    # Check for missing or important headers
    important_headers = [
        'Server', 'Transfer-Encoding', 'Connection', 'X-Powered-By', 
        'Content-Encoding', 'Cache-Control', 'Expires', 'Pragma',
        'Strict-Transport-Security', 'X-Content-Type-Options', 'X-Frame-Options',
        'X-XSS-Protection', 'Referrer-Policy', 'Permissions-Policy',
        'Access-Control-Allow-Origin', 'Set-Cookie', 'Location', 'Last-Modified', 'ETag'
    ]
    
    for header in important_headers:
        value = headers_output.get(header, 'Not present')
        
        if value == 'Not present':
            analysis['header_issues'].append(f"Missing header: {header}")
        elif header == 'Strict-Transport-Security' and 'max-age' not in value:
            analysis['header_issues'].append(f"Invalid or missing max-age in {header}")
        elif header == 'X-Content-Type-Options' and value != 'nosniff':
            analysis['header_issues'].append(f"Incorrect value for {header}: {value}")
        elif header == 'X-Frame-Options' and value != 'DENY':
            analysis['header_issues'].append(f"Incorrect value for {header}: {value}")
        elif header == 'X-XSS-Protection' and value != '1; mode=block':
            analysis['header_issues'].append(f"Incorrect value for {header}: {value}")
    
    # Check for vulnerabilities
    for vulnerability in vulnerabilities:
        library = vulnerability.get('library', 'Unknown')
        for vuln in vulnerability.get('vulnerabilities', []):
            cve = vuln.get('CVE', 'No CVE Found')
            description = vuln.get('description', 'No description')
            
            if cve != 'No CVE Found':
                analysis['vulnerability_issues'].append(f"Vulnerability found in {library}: {description} (CVE: {cve})")
    
    # Check for databases and handle missing or insecure databases
    if not databases or 'No any Databases Found' in databases:
        analysis['database_issues'].append("No databases found or accessible.")
    
    # Provide solutions for missing or incorrect headers
    solutions = {
        'Strict-Transport-Security': "Ensure the `Strict-Transport-Security` header is set to `max-age=31536000; includeSubDomains` to enforce HTTPS.",
        'X-Content-Type-Options': "Set the `X-Content-Type-Options` header to `nosniff` to prevent MIME type sniffing.",
        'X-Frame-Options': "Ensure the `X-Frame-Options` header is set to `DENY` or `SAMEORIGIN` to prevent clickjacking.",
        'X-XSS-Protection': "Set `X-XSS-Protection` to `1; mode=block` to enable the XSS filter in modern browsers.",
        'Content-Encoding': "Consider setting the `Content-Encoding` header to `gzip` to compress response data, improving performance.",
        'Cache-Control': "Set appropriate `Cache-Control` headers to prevent caching of sensitive data.",
        'Vulnerabilities': "Ensure you are using an updated version of vulnerable libraries like jQuery to avoid exploits (e.g., upgrade jQuery to version 3.5.0 or higher to fix CVE-2020-11022)."
    }
    
    # Prepare final analysis result
    final_analysis = {
        'issues': analysis,
        'solutions': solutions
    }
    
    return final_analysis

# Example of the result input
result = {
    'headers_output': {
        'Server': 'Not present', 'Date': 'Tue, 21 Jan 2025 15:30:20 GMT',
        'Content-Type': 'text/html; charset=utf-8', 'Transfer-Encoding': 'Not present', 
        'Connection': 'Not present', 'X-Powered-By': 'Not present', 'Content-Encoding': 'Not present',
        'Cache-Control': 'private', 'Expires': 'Not present', 'Pragma': 'Not present', 'Content-Length': '18368',
        'Vary': 'Not present', 'Strict-Transport-Security': 'max-age=31536000; includeSubDomains', 
        'X-Content-Type-Options': 'nosniff', 'X-Frame-Options': 'DENY', 'X-XSS-Protection': '1; mode=block', 
        'Referrer-Policy': 'no-referrer', 'Permissions-Policy': 'Not present', 
        'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': '*', 
        'Access-Control-Allow-Headers': '*', 'Access-Control-Allow-Credentials': 'true', 
        'Access-Control-Expose-Headers': 'Not present', 
        'Set-Cookie': 'ASP.NET_SessionId=h0tqfuc1g4icpgyv2olx1ifw; path=/; HttpOnly; SameSite=Lax, BIGipServerSOSYS-POOL=369103020.20480.0000; path=/; Httponly; Secure',
        'Cookie': 'Not present', 'Location': 'Not present', 'Accept-Ranges': 'Not present', 'Last-Modified': 'Not present',
        'ETag': 'Not present', 'Content-Disposition': 'Not present', 'Content-Language': 'Not present', 'X-Request-ID': 'Not present'
    },
    'vulnerabilities': [{
        'library': '/JsLibrary/jquery-1.11.1.min.js',
        'vulnerabilities': [{'CVE': 'CVE-2020-11022', 'description': 'Cross-site scripting (XSS) vulnerability in jQuery before version 3.5.0.'}]
    }],
    'databases': ['No any Databases Found']
}

# Call the function
analysis_result = analyze_headers_and_vulnerabilities(result)

# Print analysis results
from pprint import pprint
pprint(analysis_result)
