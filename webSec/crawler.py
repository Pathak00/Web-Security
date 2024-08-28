# myapp/crawler.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
import time

class DomainFetcher:
    def __init__(self, start_url):
        self.start_url = start_url
        self.base_url = urlparse(start_url).scheme + "://" + urlparse(start_url).hostname
        self.robots_txt = None
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        self.visited = set()
        self.results = []

    def fetch_robots_txt(self):
        robots_url = urljoin(self.base_url, '/robots.txt')
        try:
            response = requests.get(robots_url, headers=self.headers)
            if response.status_code == 200:
                self.robots_txt = response.text
        except requests.RequestException as e:
            print(f'Error fetching robots.txt: {e}')

    def is_allowed_by_robots(self, url):
        if not self.robots_txt:
            return True
        parsed_url = urlparse(url)
        path = parsed_url.path
        disallow_patterns = re.findall(r"Disallow:\s*(.*)", self.robots_txt, re.IGNORECASE)
        return all(not re.match(pattern.strip(), path) for pattern in disallow_patterns)

    def fetch_url(self, url, retries=3):
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                print(f'Error while fetching URL: {url} (Attempt {attempt + 1}/{retries}) (Error: {e})')
                if attempt < retries - 1:
                    time.sleep(5)
        return None

    def crawl_domain(self):
        self.fetch_robots_txt()
        response = self.fetch_url(self.start_url)
        if response:
            if response.status_code == 200:
                if self.is_allowed_by_robots(self.start_url):
                    soup = BeautifulSoup(response.text, 'html.parser')
                    self.process_page(soup)
                    return self.results
                else:
                    return [f'URL blocked by robots.txt: {self.start_url}']
            elif response.status_code == 404:
                return [f'URL not found: {self.start_url}']
            else:
                return [f'Failed to retrieve URL: {self.start_url} (Status Code: {response.status_code})']
        return ['Failed to retrieve URL']

    def process_page(self, soup):
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(self.base_url, href)
            if self.is_valid_url(full_url) and full_url not in self.visited:
                self.visited.add(full_url)
                self.results.append(full_url)

    def is_valid_url(self, url):
        parsed_url = urlparse(url)
        return parsed_url.scheme in ['http', 'https'] and parsed_url.hostname == urlparse(self.base_url).hostname
