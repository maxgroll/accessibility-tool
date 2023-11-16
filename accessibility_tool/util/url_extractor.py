# url_extractor.py

import requests
import logging
from typing import List
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_urls(url: str, base_url: str = None) -> List[str]:
    """
    Extracts all hyperlinked URLs from a given webpage.

    Args:
        url (str): The URL of the webpage to extract links from.
        base_url (str, optional): The base URL to resolve relative links against. Defaults to None.

    Returns:
        List[str]: A list of absolute URLs extracted from the page.
    """
    if base_url is None:
        base_url = url

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        logging.error(f"Error occurred while requesting URL {url}: {e}")
        return []

    urls = []

    for link in soup.find_all('a', href=True):
        href = link['href']
        
        # Resolve relative links
        if not href.startswith(('http://', 'https://')):
            href = urljoin(base_url, href)
        
        # Add the absolute URL to the list
        urls.append(href)

    return urls

# This allows the module to be used both as a script and as an importable module
if __name__ == "__main__":
    # Example usage:
    test_url = "https://example.com"
    found_urls = extract_urls(test_url)
    print(found_urls)
