import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

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


