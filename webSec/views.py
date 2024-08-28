# myapp/views.py
<<<<<<< Updated upstream

from django.shortcuts import render
from django.http import HttpResponse
from .crawler import DomainFetcher
from urllib.parse import urlparse

def is_valid_domain(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme in ['http', 'https'] and parsed_url.netloc

def land_page(request):
    if request.method == 'POST':
        domain_url = request.POST.get('name')
        if domain_url:
            if is_valid_domain(domain_url):
                fetcher = DomainFetcher(domain_url)
                results = fetcher.crawl_domain()
                result_html = '<br>'.join(results)
            else:
                result_html = 'Invalid URL'
            return HttpResponse(f'Crawling result:<br>{result_html}')
    return render(request, 'index.html')
=======
from django.shortcuts import render
from django.http import HttpResponse


def land_page(request):
    return render(request, 'index.html')


def Url_fetch(request):
    return("url fetch")


# def validate_url(url):
#     validator = URLValidator()
#     try:
#         validator(url)
#     except ValidationError:
#         return False
#     return True

# def Get_input(request):
#     if request.method == 'POST':
#         link = request.POST.get('link', '')

#         # Validate the URL
#         if not validate_url(link):
#             return render(request, 'myapp/results.html', {'result_message': 'Invalid URL format. Please enter a valid URL.'})

#         # Assuming 'param_name' is the parameter to test for SQL injection
#         param_name = 'query'  # This should be set to the actual parameter name you want to test

#         # Run SQL Injection test
#         results = test_sql_injection(link, param_name)

#         # Combine results into a single message
#         result_message = '<br>'.join(results)
#         return render(request, 'myapp/results.html', {'result_message': result_message})

#     return render(request, 'myapp/input_form.html')
>>>>>>> Stashed changes
