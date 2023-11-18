#all_urls_extractor

import logging
from urllib.parse import urljoin
from typing import Set
from .url_extractor import extract_urls
from util import is_valid_url

def extract_all_urls(url: str) -> Set[str]:
    """
    Extracts all accessible URLs from a given base URL.

    Args:
        url (str): The base URL to start the extraction from.

    Returns:
        Set[str]: A set of all extracted and accessible URLs.

    This function iteratively extracts URLs from the given base URL and its sub-pages,
    checking each URL for validity and accessibility before adding it to the set of accessible URLs.
    """
    #logging.info(f"Starting URL extraction from: {url}")
    # Initialize set for storing tested URLs and list for URLs to test
    accessible_urls = set()

    # Determine the base URL for resolving relative links
    base_url = urljoin(url, '/')

    # Set up the general directory to store accessibility test results
    #general_test_dir = 'accessibility_results'
    #os.makedirs(general_test_dir, exist_ok=True)

    # Loop through URLs to extract
    urls_to_extract = {url}  # start with base url
    while urls_to_extract:
        current_url = urls_to_extract.pop()
        # Skip testing for certain conditions
        if current_url in accessible_urls or not is_valid_url(current_url, base_url):
            continue
        #add current url to accessible urls
        #try:
        accessible_urls.add(current_url)
        #except Exception as e:
            #logging.error(f"Error occurred while getting URL {current_url}: {e}")
            #continue  # Optional: Decide whether to continue or break the loop

        # Extract more URLs from the current URL in case there are sub-pages
        try:
            extracted_urls = extract_urls(current_url)

            # Filter out external URLs and add to the list of URLs to test
            for extracted_url in extracted_urls:
                full_url = urljoin(base_url, extracted_url)
                if full_url not in accessible_urls and is_valid_url(full_url, base_url):
                    urls_to_extract.add(full_url)  # Add to set to prevent duplicates
        except Exception as e:
            logging.error(f"Error occurred while extracting URLs from {current_url}: {e}")

    #logging.info(f"Finished URL extraction from: {url}")
    # Return the results
    return accessible_urls

# for testing purposes
if __name__ == "__main__":
    # This block is for testing purposes
    test_url = "https://example.com"
    results = extract_all_urls(test_url)
    print(results)