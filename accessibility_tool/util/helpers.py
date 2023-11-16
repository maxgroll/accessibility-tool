#utils/helpers.py
import validators
import requests
import os
import logging
from datetime import datetime
from urllib.parse import urlparse, urlunparse, urljoin

import json
from bs4 import BeautifulSoup


def is_url_accessible(url: str) -> bool:
    """Check if the given URL is accessible.

    Args:
        url (str): URL to check.

    Returns:
        bool: True if the URL is accessible, False otherwise.
    """
        # pass the url into
        # request.get

    ########
    if not url.startswith(('http://', 'https://')):
        return False




    try:
        response = requests.get(url, stream=True, timeout=10)
        response.close()  # Make sure to close the response
        return response.status_code == 200
    except requests.RequestException as e:
        logging.error(f"Failed to access URL {url}: {e}")
        return False
    
def is_valid_url(url: str, base_url: str) -> bool:
    """
    Validates the given URL and checks it against certain patterns to filter out.
    
    Args:
        url (str): The URL to validate.
        base_url (str): The base URL for the website being tested.
    
    Returns:
        bool: True if the URL is valid and doesn't match filtered patterns, False otherwise.
    """
    parsed_url = urlparse(url)
    cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))

    # Check if URL is valid
    if not validators.url(cleaned_url):
        return False

    # Check if URL has a fragment (anchor) or query parameters
    if parsed_url.fragment or parsed_url.query:
        return False

    # Check if URL is within the same base URL
    if not cleaned_url.startswith(base_url):
        return False
    
    return cleaned_url.startswith(base_url)


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
    directory_path = os.path.join('accessibility_results', domain, specific_page, timestamp)
    
    # Create the directory if it doesn't exist
    os.makedirs(directory_path, exist_ok=True)
    
    return directory_path

#TODO maybe use to get a list of urls and use it to make the selection on ui
def extracted_urls_to_json(url, filename):
    """
    Saves a list of URLs to a JSON file.

    Args:
        urls (list): A list of URLs to save.
        filename (str): The name of the file to save the URLs to.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    extracted_urls = set()
    ordered_urls = []

    base_url = urljoin(url, '/')
    
    # Extract URLs from anchor tags
    for anchor in soup.find_all("a"):
        href = anchor.get("href")
        if href and "#" not in href and not href.endswith((".jpg", 
                                                           ".jpeg", ".png", ".gif")):
            extracted_url = urljoin(url, href)
            if extracted_url.startswith(base_url):
                extracted_urls.add(extracted_url)

    ordered_urls = [base_url] + list(extracted_urls - {base_url})

    with open(filename, 'w') as file:
        # Save results in JSON format
            file.write(json.dumps(ordered_urls, indent=4))
            file.write('\n')
    
    return None