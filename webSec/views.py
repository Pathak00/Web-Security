# webSec/views.py

import requests
from django.shortcuts import render
from django.http import HttpResponse

# List of common SQL injection payloads
SQL_INJECTION_PAYLOADS = [
    "' OR '1'='1",
    "' OR '1'='1' --",
    "' OR '1'='1' /*",
    "' OR 1=1--",
    "' OR 1=1#",
    "' OR 1=1/*",
    "' OR 'x'='x",
    "' OR 'x'='x' --",
    "' OR 'x'='x' /*",
]

def check_sql_injection(website_url):
    results = []
    for payload in SQL_INJECTION_PAYLOADS:
        try:
            # Send GET request with the payload
            response = requests.get(website_url, params={'id': payload}, timeout=5)
            
            if "error" in response.text or "syntax" in response.text or "SQL" in response.text:
                results.append(f"Possible SQL Injection vulnerability detected with payload: {payload}")
            else:
                results.append(f"No vulnerability detected with payload: {payload}")
        except requests.exceptions.RequestException as e:
            results.append(f"Error checking {website_url} with payload {payload}: {str(e)}")

    return results

def index(request):
    if request.method == 'POST':
        website_url = request.POST.get('website_url')
        if website_url:
            results = check_sql_injection(website_url)
            return render(request, 'index.html', {'results': results, 'url': website_url})
    return render(request, 'index.html')
