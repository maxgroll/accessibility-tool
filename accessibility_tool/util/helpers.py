#utils/helpers.py
import validators
import requests

from datetime import datetime
import os

from urllib.parse import urlparse



def is_url_accessible(url):
    """Check if the given URL is accessible.

    Args:
        url (str): URL to check.

    Returns:
        bool: True if the URL is accessible, False otherwise.
    """
    try:
        response = requests.head(url, allow_redirects=True)
        return response.status_code == 200
    except requests.RequestException:
        return False
    
def is_valid_url(url, base_url):
    """
    Validates the given URL and checks it against certain patterns to filter out.
    
    Args:
        url (str): The URL to validate.
        base_url (str): The base URL for the website being tested.
    
    Returns:
        bool: True if the URL is valid and doesn't match filtered patterns, False otherwise.
    """
    # Check if URL is valid
    if not validators.url(url):
        return False

    # Check if URL is an internal anchor or empty
    if url.startswith('#') or not url.strip():
        return False

    # Check if URL is a parametrized search URL
    if any(param in url for param in ['?q=', '?search=', '&q=', '&search=', '#']):
        return False

    # Check if URL is within the same base URL
    if not url.startswith(base_url):
        return False

    return True

def url_to_dir_name(url):
    """
    Converts a URL to a directory-friendly name by removing non-alphanumeric characters.

    Args:
        url (str): The URL to convert.

    Returns:
        str: A directory-friendly version of the URL.
    """
    # Remove all non-alphanumeric characters (excluding periods and slashes)
    url = url.replace('http://', '').replace('https://', '')

    # Ersetzen von Punkten und anderen Nicht-Buchstaben/Zahlen durch Unterstriche
    url = ''.join('_' if not e.isalnum() else e for e in url).strip('_')

    #timestamp = datetime.now().strftime("%Y-%m-%d____%H-%M")
    #return f"{url}{timestamp}"
    return url


def create_test_directory(url):
    """
    Creates a nested directory structure for test results based on the given URL.
    The structure will be: accessibility_results/domain/specific_page/timestamp/
    
    Args:
        url (str): The full URL for which to create the directory structure.
        
    Returns:
        str: The path to the directory for the specific test.
    """
    # Parse the base domain from the URL
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace('www.', '')
    
    # Create a directory-friendly name for the specific page
    specific_page = parsed_url.path.strip('/').replace('/', '_') or 'homepage'
    
    # Create a timestamp for uniqueness
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Combine all parts to create the nested directory structure
    directory_path = os.path.join('accessibility_results', domain, specific_page, timestamp)
    
    # Create the directory if it doesn't exist
    os.makedirs(directory_path, exist_ok=True)
    
    return directory_path



