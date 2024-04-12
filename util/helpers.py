#utils/helpers.py

import validators
import requests
import os
import logging
from datetime import datetime
from urllib.parse import urlparse, urlunparse
from urllib.robotparser import RobotFileParser

from config import FULL_ACCESSIBILITY_RESULTS_DIRECTORY

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
    The structure will be: data/accessibility_tests/domain/timestamp/

    Args:
        url (str): The full URL for which to create the directory structure.
        
    Returns:
        str: The path to the directory for the specific test-session.
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace('www.', '')

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    directory_path = os.path.join(FULL_ACCESSIBILITY_RESULTS_DIRECTORY, domain, timestamp)
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
    cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))

    if not validators.url(cleaned_url):
        logging.debug(f"URL failed validation: {url}")
        return False

    if parsed_url.scheme not in ['http', 'https']:
        logging.debug(f"URL scheme not supported: {url}")
        return False

    if parsed_url.fragment or parsed_url.query:
        logging.debug(f"URL has fragment or query: {url}")
        return False

    ignored_extensions = ['.pdf', '.jpg', 'jpeg', 'webp', '.png', '.svg', '.css', '.js', '.xml']
    if any(parsed_url.path.lower().endswith(ext) for ext in ignored_extensions):
        logging.debug(f"URL has ignored extension: {url}")
        return False
    
    if not url.startswith(base_url):
        logging.debug(f"URL does not start with base URL: {url}")
        return False

    try:
        response = session.head(cleaned_url, allow_redirects=True, timeout=10)
        if 'text/html' not in response.headers.get('Content-Type', ''):
            logging.debug(f"URL rejected due to content type: {url}")
            return False
    except requests.RequestException as e:
        logging.warning(f"Failed to fetch URL headers for {url}: {e}")
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
    rp = RobotFileParser()

    # Fetch and log the contents of robots.txt
    try:
        response = requests.get(robots_url)
        if response.status_code == 200:
            #logging.info(f"Contents of robots.txt: {response.text}")
            rp.parse(response.text.splitlines())
        else:
            logging.info(f"No robots.txt found at {robots_url}. Assuming crawling is allowed.")
            return True
    except requests.RequestException as e:
        logging.error(f"Error fetching robots.txt: {e}")
        return True  # Assume crawling is allowed if there's an error fetching robots.txt

    # Check if fetching is allowed
    allowed = rp.can_fetch(user_agent, url)
    if not allowed:
        logging.debug(f"Fetching disallowed by robots.txt: {url} for user-agent {user_agent}")
    else:
        logging.debug(f"Fetching allowed by robots.txt: {url} for user-agent {user_agent}")
    return allowed


def get_latest_results_directory(base_results_directory):
    domain_directories = os.listdir(base_results_directory)
    latest_time = datetime.min
    latest_directory = None

    for domain_dir in domain_directories:
        full_domain_path = os.path.join(base_results_directory, domain_dir)
        if os.path.isdir(full_domain_path):  # Ensure it's a directory
            # Get all timestamped directories within the domain directory
            timestamps = [d for d in os.listdir(full_domain_path) if os.path.isdir(os.path.join(full_domain_path, d))]
            for ts in timestamps:
                # Parse the timestamp from the directory name
                try:
                    ts_time = datetime.strptime(ts, "%Y-%m-%d_%H-%M-%S")
                    if ts_time > latest_time:
                        latest_time = ts_time
                        latest_directory = os.path.join(full_domain_path, ts)
                except ValueError:
                    # Handle directories that don't match the timestamp format
                    continue
    
    return latest_directory
