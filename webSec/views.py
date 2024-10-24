# myapp/views.py

from django.shortcuts import render
from django.http import HttpResponse
from .crawler import DomainFetcher
from urllib.parse import urlparse
import socket


def land_page(request):
    if request.method == 'POST':
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




