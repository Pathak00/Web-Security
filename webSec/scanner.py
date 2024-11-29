from bs4 import BeautifulSoup
import requests

def get_javascript_libraries(url):
    """Extract JavaScript libraries from a given URL."""
    libraries = []
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')

        for script in scripts:
            src = script.get('src', '')
            if src:
                # Example check for common libraries
                if 'jquery' in src or 'bootstrap' in src or 'vue' in src:
                    libraries.append(src)
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")

    return libraries


def check_vulnerabilities(library_list):
    """Check for known vulnerabilities of listed libraries."""
    vulnerabilities = []
    # This is a placeholder function. Replace with actual API calls to services like Snyk or CVE databases.
    for library in library_list:
        # Mock vulnerability check
        if 'jquery' in library:
            vulnerabilities.append({
                'library': library,
                'vulnerabilities': [
                    {'CVE': 'CVE-2020-11022', 'description': 'Cross-site scripting (XSS) vulnerability.'}
                ]
            })
        elif 'bootstrap' in library:
            vulnerabilities.append({
                'library': library,
                'vulnerabilities': [
                    {'CVE': 'CVE-2019-8331', 'description': 'Security issue related to Bootstrap.'}
                ]
            })
    return vulnerabilities
