#utils/helpers.py

import validators
import requests
import os
import logging
from datetime import datetime
from urllib.parse import urlparse, urlunparse
from urllib.robotparser import RobotFileParser

from data.config import FULL_ACCESSIBILITY_RESULTS_DIRECTORY


def is_url_accessible(url: str) -> bool:
    """Check if the given URL is accessible.

    Args:
        url (str): URL to check.

    Returns:
        bool: True if the URL is accessible, False otherwise.
    """ 
    if not url.startswith(('http://', 'https://')):
        return False

    try:
        response = requests.get(url, stream=True, timeout=10)
        response.close()  # Make sure to close the response
        return response.status_code == 200
    except requests.RequestException as e:
        logging.error(f"Failed to access URL {url}: {e}")
        return False
    

def create_test_directory(url: str) -> str:
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
    directory_path = os.path.join(FULL_ACCESSIBILITY_RESULTS_DIRECTORY, domain, specific_page, timestamp)
    
    # Create the directory if it doesn't exist
    os.makedirs(directory_path, exist_ok=True)
    
    return directory_path


def is_valid_url(url: str, base_url: str, session: requests.Session) -> bool:
    """
    Validates a URL based on specific criteria and content type check.

    Args:
        url (str): The URL to validate.
        base_url (str): The base URL of the target website.
        session (requests.Session): The requests session for making HTTP requests.

    Returns:
        bool: True if the URL is valid and points to a webpage, False otherwise.
    """
    parsed_url = urlparse(url)

    # Check if URL is valid
    if not validators.url(parsed_url):
        return False

    # ignore URLs, that do not start with http or https
    if parsed_url.scheme not in ['http', 'https']:
        return False

    # Ignore URLs with fragment or query parameters
    if parsed_url.fragment or parsed_url.query:
        return False

    # Ignore URLs with unwanted extensions
    ignored_extensions = ['.pdf', '.jpg', 'jpeg', 'webp', '.png', '.svg', '.css', '.js', '.xml']
    if any(parsed_url.path.lower().endswith(ext) for ext in ignored_extensions):
        return False
    
    # validate if URL starts with the base url
    if not url.startswith(base_url):
        return False

    # Check content type of URL to make shure only pages are passed to the tests
    cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
    try:
        response = session.head(cleaned_url, allow_redirects=True, timeout=10)
        if 'text/html' not in response.headers.get('Content-Type', ''):
            return False
    except requests.RequestException as e:
        logging.warning(f"Failed to fetch URL headers: {e}")
        return False

    return True


def can_fetch(url: str, user_agent: str = '*') -> bool:
    """
    Checks if a URL can be fetched based on the website's robots.txt file.

    Args:
        url (str): The URL to check.
        user_agent (str): The user agent of the crawler (default is '*').

    Returns:
        bool: True if fetching the URL is allowed, False otherwise.
    """
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    rp = RobotFileParser(robots_url)
    rp.set_url(robots_url)
    rp.read()

    return rp.can_fetch(user_agent, url)