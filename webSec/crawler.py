# myapp/crawler.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
import time
from django.db import connection
import pymysql
import datetime
from django.shortcuts import render



class DomainFetcher:
    def __init__(self, start_url):
        self.start_url = start_url
        self.base_url = urlparse(start_url).scheme + "://" + urlparse(start_url).hostname
        self.robots_txt = None
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        self.visited = set()
        self.results = []
      

##robotos.txt check 

    def fetch_robots_txt(self):
        robots_url = urljoin(self.base_url, '/robots.txt')
        try:
            response = requests.get(robots_url, headers=self.headers)
            if response.status_code == 200:
                self.robots_txt = response.text
                return True
            else:
                print("robonotpresent")
                return False
        except requests.RequestException as e:
            print(f'Error fetching robots.txt: {e}')

    def is_robotstxt_present(self, url):
        if  self.robots_txt:
            return True
        return False
     
#to check the url responding or not
    def fetch_url_Reponse(self, url, retries=3):
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
        response = self.fetch_url_Reponse(self.start_url)
        if response:
            if response.status_code == 200:
                if not self.fetch_robots_txt():
                    soup = BeautifulSoup(response.text, 'html.parser')
                    self.process_page(soup)
                    
                    # for url in self.results:
                    #     severity=self.check_sql_injection(url)
                    # return render(self, 'result.html', {'severity': severity, 'url': url})
                    return self.results
                else:
                    parsed_url = urlparse(self.start_url)
                    path = parsed_url.path
                    Allow_patterns =re.findall(r"^\s*Allow:\s*(.*)", self.robots_txt, re.IGNORECASE | re.MULTILINE)
                    Disallow_patterns =re.findall(r"^\s*Disallow:\s*(.*)", self.robots_txt, re.IGNORECASE | re.MULTILINE)
                    print(Disallow_patterns)
                    if Allow_patterns:
                        print("test allow?")
                        print(Allow_patterns)
                        
                        # if '/' in Allow_patterns:
                        #     soup = BeautifulSoup(response.text, 'html.parser')
                        #     self.process_page(soup)
                        # return self.results
                        
                        for pattern in Allow_patterns:
                            url_to_visit = urljoin(self.base_url, pattern.strip())
                            url_to_visit=self.filter_url(url_to_visit)
                            if self.is_valid_url(url_to_visit) and url_to_visit not in self.results:
                                if self.check_response(url_to_visit):
                                    if self.is_same_domain(url_to_visit):
                                        self.results.append(url_to_visit)
                                    # severity=self.check_sql_injection(url_to_visit)
                        return self.results
                    # elif len(Allow_patterns) <= 1:
                    #     soup = BeautifulSoup(response.text, 'html.parser')
                    #     self.process_page(soup)
                    #     for url in self.results:
                    #         # severity=self.check_sql_injection(url)
                    #         return self.results
                    elif not Disallow_patterns or all(x == '' for x in Disallow_patterns):
                        print("disllow empty?")
                        soup = BeautifulSoup(response.text, 'html.parser')
                        self.process_page(soup)
                        return self.results    
                    else:
                        return ["There's no any Allowed URL in Robots.txt"]
            elif response.status_code == 404:
                return [f'URL not found: {self.start_url}']
            else:
                return [f'Failed to retrieve URL: {self.start_url} (Status Code: {response.status_code})']
        return ['Failed, Please Check URL is it Domain?']

    def process_page(self, soup):
        print(soup)
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(self.base_url, href)
            if self.is_valid_url(full_url) and full_url not in self.visited:
                if self.is_same_domain(full_url):
                    filtered_url = self.filter_url(full_url)
                    if self.check_response(filtered_url):
                        print("valid")
                        self.visited.add(full_url)
                        self.results.append(full_url)
            print(self.results)
        return self.results 
                    
    def is_same_domain(self, url):
        base_hostname = urlparse(self.base_url).hostname
        target_hostname = urlparse(url).hostname
        print(target_hostname)
        print(base_hostname)
        return base_hostname == target_hostname

    def check_response(self, url):
        try:
            response = requests.get(url, timeout=3)
            print(url)
            print(response)
            if response.status_code==200:
                return True
            else:
                False
        except requests.RequestException:
            return False
        
        
# to check the https and http 
    def is_valid_url(self, url):
        parsed_url = urlparse(url)
        given_hostname = parsed_url.hostname
        base_hostname = urlparse(self.base_url).hostname
        return parsed_url.scheme in ['http', 'https'] 

    
    def is_valid_domain(self,url):
        parsed_url = urlparse(url)
        return parsed_url.scheme in ['http', 'https'] and parsed_url.netloc
    
    def filter_url(self,url):
        parsed_url = urlparse(url)
        path_parts = [part for part in parsed_url.path.strip('/').split('/') if part]

        if path_parts:
            print(path_parts)
            filtered_path = f"/{path_parts[0]}"  # Retain the first part with a trailing slash
        else:
            filtered_path = "/"  # Fallback to root if no path parts
    
        filtered_url = f"{parsed_url.scheme}://{parsed_url.hostname}{filtered_path}"
        return filtered_url
    
  

    def check_sql_injection(self, url):
        sql_injection_payloads = [
            "'", '"', "--", "#", "/*", "*/", "OR 1=1", "OR 'a'='a'", "DROP TABLE", "SELECT * FROM", 
            "UNION SELECT", "1=1", "AND 1=1", "AND 'a'='a'", "AND 1=1--", "' OR 1=1--", '" OR 1=1--'
        ]

        # Loop through each payload and test the URL
        for payload in sql_injection_payloads:
            # Append the payload to the URL (assuming a GET request with query parameters)
            test_url = f"{url}{payload}"
            print(f"Testing URL: {test_url}")

            try:
                response = requests.get(test_url)

                # Check for common SQL error signs or abnormal responses
                if response.status_code == 200:  # Successful request
                    error_signs = ['mysql', 'syntax', 'error', 'warning', 'exception', 'sql', 'unexpected']

                    # If SQL error is detected, return severity 'High'
                    if any(error_word in response.text.lower() for error_word in error_signs):
                        print(f"SQL Injection vulnerability detected in URL: {test_url}")
                        return "High"  # Return severity level as "High"
                    else:
                        print(f"No obvious SQL injection vulnerability in URL: {test_url}")

                else:
                    # Handle non-200 status codes
                    print(f"Received non-200 response: {response.status_code} for URL: {test_url}")

            except requests.exceptions.RequestException as e:
                print(f"Error during request to {test_url}: {e}")

        # If no vulnerability was found after checking all payloads
        print(f"No SQL Injection vulnerability detected for URL: {url}")
        return "Low"  # Return lower severity if no issue is found
