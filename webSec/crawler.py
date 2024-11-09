# myapp/crawler.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
import time
from django.db import connection
import pymysql

class DomainFetcher:
    def __init__(self, start_url):
        self.start_url = start_url
        self.base_url = urlparse(start_url).scheme + "://" + urlparse(start_url).hostname
        self.robots_txt = None
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        self.visited = set()
        self.results = []
      

    def execute_query(self,query):
        try:
            connection = pymysql.connect(
                host='127.0.0.1',
                user='root',          # Your database username
                password='',          # Your database password
                db='mydb',           # Your database name
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            with connection:
                cursor = connection.cursor()
                cursor.execute(query)
                # Fetching results
                results = cursor.fetchall()
                print("Connection successful!")
                return results
        except Exception as e:
            print(f"Connection failed: {e}")
            return None


    def fetch_robots_txt(self):
        robots_url = urljoin(self.base_url, '/robots.txt')
        try:
            response = requests.get(robots_url, headers=self.headers)
            if response.status_code == 200:
                self.robots_txt = response.text
          
        except requests.RequestException as e:
            print(f'Error fetching robots.txt: {e}')

    def is_robotstxt_present(self, url):
        if  self.robots_txt:
            return True
        return False
        # parsed_url = urlparse(url)
        # path = parsed_url.path
        # disallow_patterns = re.findall(r"^\s*Allow:\s*(.*)", self.robots_txt, re.IGNORECASE)
        # print(disallow_patterns)
        # return all(not re.match(pattern.strip(), path) for pattern in disallow_patterns)

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
                if self.is_robotstxt_present(self.start_url):
                    soup = BeautifulSoup(response.text, 'html.parser')
                    self.process_page(soup)
                    return self.results
                else:
                    parsed_url = urlparse(self.start_url)
                    path = parsed_url.path
                    Allow_patterns =re.findall(r"^\s*Allow:\s*(.*)", self.robots_txt, re.IGNORECASE | re.MULTILINE)
                  
                    if Allow_patterns:  
                        for pattern in Allow_patterns:
                            url_to_visit = urljoin(self.base_url, pattern.strip())
                            url_to_visit=self.filter_url(url_to_visit)
                            if self.is_valid_url(url_to_visit) and url_to_visit not in self.results:
                                self.results.append(url_to_visit)
                        return self.results
                    elif len(Allow_patterns) <= 1:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        self.process_page(soup)
                        return self.results
                    else:
                        return ['No Allowed URLby Robots.txt']
            elif response.status_code == 404:
                return [f'URL not found: {self.start_url}']
            else:
                return [f'Failed to retrieve URL: {self.start_url} (Status Code: {response.status_code})']
        return ['Failed to retrieve Please Check URL']

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

    def is_valid_domain(self,url):
        parsed_url = urlparse(url)
        print(parsed_url)
        return parsed_url.scheme in ['http', 'https'] and parsed_url.netloc
    
    def filter_url(self,url):
        parsed_url = urlparse(url)
        path_parts = [part for part in parsed_url.path.strip('/').split('/') if part]

        if path_parts:
            print(path_parts)
            filtered_path = f"/{path_parts[0]}/"  # Retain the first part with a trailing slash
        else:
            filtered_path = "/"  # Fallback to root if no path parts
    
        filtered_url = f"{parsed_url.scheme}://{parsed_url.hostname}{filtered_path}"
        return filtered_url
    
    