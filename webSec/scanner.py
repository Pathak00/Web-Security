from bs4 import BeautifulSoup
import requests
import re

LATEST_VERSIONS = {
    'jquery': '3.6.0',
    'bootstrap': '5.3.0',
    'vue': '3.3.0',
    'react': '18.2.0',
    'angular': '16.0.0',
    'lodash': '4.17.21'
}

def extract_version(library_name, url):
    """Extracts the version from the script URL using regex (if available)."""
    # Regex patterns to find version numbers (very simplistic version matching)
    patterns = {
        'jquery': r'jquery[-_]([0-9]+\.[0-9]+\.[0-9]+)',
        'bootstrap': r'bootstrap[-_]([0-9]+\.[0-9]+\.[0-9]+)',
        'vue': r'vue[-_]([0-9]+\.[0-9]+\.[0-9]+)',
        'react': r'react[-_]([0-9]+\.[0-9]+\.[0-9]+)',
        'angular': r'angular[-_]([0-9]+\.[0-9]+\.[0-9]+)',
        'lodash': r'lodash[-_]([0-9]+\.[0-9]+\.[0-9]+)',
    }

    # Check if there's a regex pattern for the library
    if library_name in patterns:
        match = re.search(patterns[library_name], url)
        if match:
            return match.group(1)  # Return the matched version
    return None

def get_javascript_libraries(url):
    """Extract JavaScript libraries from a given URL and check if they are outdated."""
    libraries = []
    outdated_libraries = []
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')

        for script in scripts:
            src = script.get('src', '')
            if src:
                # Check for common libraries
                for lib in LATEST_VERSIONS:
                    if lib in src.lower():
                        version = extract_version(lib, src)
                        if version:
                            # Add to libraries list
                            libraries.append(src)

                            # Check if the library is outdated
                            if version != LATEST_VERSIONS[lib]:
                                outdated_libraries.append({
                                    'library': lib,
                                    'found_version': version,
                                    'latest_version': LATEST_VERSIONS[lib],
                                    'url': src
                                })
    
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")

    # Return both the libraries and the outdated libraries
    return libraries


def check_vulnerabilities(library_list):
    """Check for known vulnerabilities of listed libraries."""
    vulnerabilities = []
    
    # Iterate through the list of libraries
    for library in library_list:
        library_vulnerabilities = []  # List to store vulnerabilities for the current library
        
        # Mock vulnerability check (Replace with actual API calls or database queries)
        if 'jquery' in library:
            library_vulnerabilities.append({
                'CVE': 'CVE-2020-11022',
                'description': 'Cross-site scripting (XSS) vulnerability.'
            })
        elif 'bootstrap' in library:
            library_vulnerabilities.append({
                'CVE': 'CVE-2019-8331',
                'description': 'Security issue related to Bootstrap.'
            })
        
        # If vulnerabilities exist for the library, add them to the vulnerabilities list
        if library_vulnerabilities:
            vulnerabilities.append({
                'vulnerabilities': library_vulnerabilities
            })
    
    return vulnerabilities
