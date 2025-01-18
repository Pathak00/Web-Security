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

def calculate_severity(headers):
    """
    Calculate the total severity level based on the presence or absence of specific HTTP headers.
    Headers will be assigned severity levels categorized as High, Medium, or Low.
    
    Args:
    headers (dict): Dictionary of HTTP headers returned by a request.
    
    Returns:
    str: The overall severity level - "High", "Medium", or "Low".
    """
    # Define the headers and their corresponding severity levels
    header_severity = {
        "Strict-Transport-Security": "High",  # Critical security header (HSTS)
        "X-Frame-Options": "High",  # Critical security header (Clickjacking protection)
        "X-XSS-Protection": "High",  # Critical security header (XSS protection)
        "X-Content-Type-Options": "Medium",  # Medium importance (prevents MIME sniffing)
        "Referrer-Policy": "Medium",  # Medium importance (controls referrer information)
        "Cache-Control": "Low",  # Less critical (prevents caching of sensitive data)
        "Content-Type": "Low",  # Less critical (defines the content type of the response)
        "Access-Control-Allow-Origin": "Low",  # Less critical (related to CORS)
    }

    # Initialize a dictionary to track severity counts
    severity_count = {
        "High": 0,
        "Medium": 0,
        "Low": 0
    }
    
    # Count the severity based on missing headers
    for header, severity in header_severity.items():
        if header not in headers or headers[header] == "Not present":
            severity_count[severity] += 1

    
    # Check for the highest severity count
    if severity_count["High"] > severity_count["Medium"] and severity_count["High"] > severity_count["Low"]:
        return "High"
    elif severity_count["Medium"] > severity_count["Low"]:
        return "Medium"
    elif severity_count["Low"] > severity_count["High"] and severity_count["Low"] > severity_count["Medium"]:
        return "Low"
    else:
        return "No critical issues"


def check_website_headers(url):
    """
    Fetch the headers from the website URL and calculate the overall severity level based on missing headers.
    
    Args:
    url (str): The URL of the website to check headers for.
    
    Returns:
    str: Overall severity level of the website - "High", "Medium", or "Low".
    """
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Get the response headers
        headers = response.headers
        
        # Calculate the overall severity level based on the headers
        severity = calculate_severity(headers)
        
        return severity
        
    except requests.RequestException as e:
        return f"Error: {str(e)}"