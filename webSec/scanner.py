from bs4 import BeautifulSoup
import requests
import re

LATEST_VERSIONS = {
    'jquery': '3.6.0',
    'bootstrap': '5.3.0',
    'vue': '3.3.0',
    'react': '18.2.0',
    'angular': '16.0.0',
    'lodash': '4.17.21',
    'axios': '1.3.0',
    'moment': '2.29.1',
    'd3': '7.7.0',
    'underscore': '1.13.1',
    'chartjs': '3.9.1',
    'semantic-ui': '2.4.2',
    'tailwindcss': '3.0.0',
    'foundation': '6.7.5',
    'sweetalert2': '11.6.0',
    'popper': '2.11.6',
    'vue-router': '4.1.6',
    'redux': '4.2.0',
    'swiper': '8.0.6'
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
        'axios': r'axios[-_]([0-9]+\.[0-9]+\.[0-9]+)',
        'moment': r'moment[-_]([0-9]+\.[0-9]+\.[0-9]+)',
        'd3': r'd3[-_]([0-9]+\.[0-9]+\.[0-9]+)',
        'underscore': r'underscore[-_]([0-9]+\.[0-9]+\.[0-9]+)',
        'chartjs': r'chartjs[-_]([0-9]+\.[0-9]+\.[0-9]+)',
        'semantic-ui': r'semantic-ui[-_]([0-9]+\.[0-9]+\.[0-9]+)',
        'tailwindcss': r'tailwindcss[-_]([0-9]+\.[0-9]+\.[0-9]+)',
        'foundation': r'foundation[-_]([0-9]+\.[0-9]+\.[0-9]+)',
        'sweetalert2': r'sweetalert2[-_]([0-9]+\.[0-9]+\.[0-9]+)',
        'popper': r'popper[-_]([0-9]+\.[0-9]+\.[0-9]+)',
        'vue-router': r'vue-router[-_]([0-9]+\.[0-9]+\.[0-9]+)',
        'redux': r'redux[-_]([0-9]+\.[0-9]+\.[0-9]+)',
        'swiper': r'swiper[-_]([0-9]+\.[0-9]+\.[0-9]+)',
        'knockout': r'knockout[-_]([0-9]+\.[0-9]+\.[0-9]+)',
    }

    # Check if there's a regex pattern for the library
    if library_name in patterns:
        match = re.search(patterns[library_name], url)
        if match:
            return match.group(1)  # Return the matched version
    return None

def get_javascript_libraries(url):
    print("test urlin lir",url)
    """Extract JavaScript libraries from a given URL and check if they are outdated."""
    libraries = [] 
    outdated_libraries = []
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        print("Response")
        print(response)
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')
        print("scripts")
        print(scripts)
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
                            
    except requests.RequestException as e:
       libraries=[]
       return libraries
        # print(f"Error fetching the URL: {e}")

    return libraries


def check_vulnerabilities(library_list):
    """Check for known vulnerabilities of listed libraries."""
    vulnerabilities = []
    
    # Debugging: Print the libraries being checked
    print(f"Checking vulnerabilities for the following libraries: {library_list}")

    # Iterate through the list of libraries
    for library in library_list:
        library_vulnerabilities = []  # List to store vulnerabilities for the current library
        
        # Mock vulnerability check (Replace with actual API calls or database queries)
        if 'jquery' in library:
            library_vulnerabilities.append({
                'CVE': 'CVE-2020-11022',
                'description': 'Cross-site scripting (XSS) vulnerability in jQuery before version 3.5.0.'
            })
        elif 'bootstrap' in library:
            library_vulnerabilities.append({
                'CVE': 'CVE-2019-8331',
                'description': 'Security issue related to Bootstrap before version 4.3.1.'
            })
        elif 'vue' in library:
            library_vulnerabilities.append({
                'CVE': 'CVE-2011-3385',
                'description': 'Cross-site scripting (XSS) vulnerability in Vue.js versions before 2.6.12.'
            })
        elif 'react' in library:
            library_vulnerabilities.append({
                'CVE': 'CVE-2020-11022',
                'description': 'Potential XSS vulnerability in React.js before version 16.12.0.'
            })
        elif 'angular' in library:
            library_vulnerabilities.append({
                'CVE': 'CVE-2020-7927',
                'description': 'Security vulnerability in Angular before version 9.1.4.'
            })
        elif 'lodash' in library:
            library_vulnerabilities.append({
                'CVE': 'CVE-2019-10744',
                'description': 'Prototype pollution vulnerability in Lodash versions before 4.17.11.'
            })
        elif 'axios' in library:
            library_vulnerabilities.append({
                'CVE': 'CVE-2020-28168',
                'description': 'Potential SSRF vulnerability in Axios versions before 0.21.1.'
            })
        elif 'moment' in library:
            library_vulnerabilities.append({
                'CVE': 'CVE-2020-28196',
                'description': 'Denial of Service vulnerability in Moment.js before version 2.29.1.'
            })
        elif 'd3' in library:
            library_vulnerabilities.append({
                'CVE': 'CVE-2020-7608',
                'description': 'Cross-Site Scripting (XSS) vulnerability in D3.js versions before 6.7.0.'
            })
        elif 'underscore' in library:
            library_vulnerabilities.append({
                'CVE': 'CVE-2019-10744',
                'description': 'Prototype pollution vulnerability in Underscore.js versions before 1.9.2.'
            })
        elif 'chartjs' in library:
            library_vulnerabilities.append({
                'CVE': 'CVE-2021-32817',
                'description': 'Cross-site scripting (XSS) vulnerability in Chart.js before version 3.7.1.'
            })
        elif 'semantic-ui' in library:
            library_vulnerabilities.append({
                'CVE': 'CVE-2018-15725',
                'description': 'Cross-Site Scripting (XSS) vulnerability in Semantic UI before version 2.4.2.'
            })
        elif 'tailwindcss' in library:
            library_vulnerabilities.append({
                'CVE': 'CVE-2021-23450',
                'description': 'Cross-site scripting (XSS) vulnerability in Tailwind CSS versions before 2.0.0.'
            })
        elif 'foundation' in library:
            library_vulnerabilities.append({
                'CVE': 'CVE-2019-8331',
                'description': 'Security issue related to Foundation framework before version 6.7.5.'
            })
        elif 'sweetalert2' in library:
            library_vulnerabilities.append({
                'CVE': 'CVE-2020-13925',
                'description': 'XSS vulnerability in SweetAlert2 before version 9.0.0.'
            })
        elif 'popper' in library:
            library_vulnerabilities.append({
                'CVE': 'CVE-2018-20677',
                'description': 'Cross-Site Scripting (XSS) vulnerability in Popper.js versions before 1.16.0.'
            })
        elif 'vue-router' in library:
            library_vulnerabilities.append({
                'CVE': 'CVE-2020-11022',
                'description': 'XSS vulnerability in Vue Router before version 3.4.9.'
            })
        elif 'redux' in library:
            library_vulnerabilities.append({
                'CVE': 'CVE-2020-7686',
                'description': 'Security vulnerability in Redux before version 4.0.5.'
            })
        elif 'swiper' in library:
            library_vulnerabilities.append({
                'CVE': 'CVE-2021-23398',
                'description': 'XSS vulnerability in Swiper before version 6.8.4.'
            })
        elif 'knockout' in library:
            library_vulnerabilities.append({
                'CVE': 'CVE-2015-1234',  # Replace with actual CVE if found
                'description': 'Vulnerability in Knockout.js 3.1.0 related to XSS or other issues.'
            })
        
        # If vulnerabilities exist for the library, add them to the vulnerabilities list
        if library_vulnerabilities:
            vulnerabilities.append({
                'library': library,
                'vulnerabilities': library_vulnerabilities
            })
    # print("vulnerabilities result")
    # print(vulnerabilities)
    return  vulnerabilities
