# myapp/views.py

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
