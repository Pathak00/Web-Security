import requests
from django.http import HttpResponse

def scan_website_headers(url):
    important_headers = [
        'Content-Type', 'Content-Length', 'Server', 'Date', 'Cache-Control',
        'Strict-Transport-Security', 'X-Content-Type-Options', 'X-Frame-Options',
        'X-XSS-Protection', 'Referrer-Policy', 'Access-Control-Allow-Origin',
        'Location', 'Accept-Ranges', 'Vary', 'Connection'
    ]
    
  
    headers_dict = {}

    try:
     
        response = requests.get(url)

        if response.status_code == 200:
            # If the request was successful, iterate over the important headers
            for header in important_headers:
                if header in response.headers:
                    headers_dict[header] = response.headers[header]
                else:
                    headers_dict[header] = 'Not present'

        else:
            # If the status code is not 200, add an error message to the dictionary
            headers_dict["Error"] = f"Failed to retrieve website. Status code: {response.status_code}"

    except requests.exceptions.RequestException as e:
        # If an exception occurs (e.g., network error), store the error in the dictionary
        headers_dict["Error"] = f"Error occurred: {e}"

    # Return the dictionary containing header names and values (or error message)
    return headers_dict