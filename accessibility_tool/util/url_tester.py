# url_tester.py

import os
import logging
from urllib.parse import urljoin
from typing import Dict, List
from .accessibility_tester import run_accessibility_tests
from .url_extractor import extract_urls
from .helpers import is_valid_url
from .helpers import create_test_directory


def extract_and_test_urls(url: str) -> Dict[str, List[str]]:
    """
    Extracts URLs from a given base URL and performs accessibility tests on them.

    Args:
        url (str): The base URL to extract links from and test.
    
    Returns:
        Dict[str, List[str]]: A dictionary containing a list of tested URLs.
    
    Raises:
        Exception: An error occurred while testing the URL..
    """
    logging.info(f"Starting URL extraction and testing from: {url}")
    # Initialize set for storing tested URLs and list for URLs to test
    tested_urls = set()

    # Determine the base URL for resolving relative links
    base_url = urljoin(url, '/')

    # Set up the general directory to store accessibility test results
    general_test_dir = 'accessibility_results'
    os.makedirs(general_test_dir, exist_ok=True)

    # Loop through URLs to test
    urls_to_test = {url}  # start with base url
    while urls_to_test:
        current_url = urls_to_test.pop()
        print(f"Testing {current_url}")
        # Skip testing for certain conditions
        if current_url in tested_urls or not is_valid_url(current_url, base_url):
            continue
        #Create a directory for this URL's test results
        test_directory = create_test_directory(current_url)

        # Perform accessibility tests and handle exceptions
        try:
            #run_accessibility_tests(current_url)
            run_accessibility_tests(current_url, test_directory)
            tested_urls.add(current_url)
        except Exception as e:
            logging.error(f"Error occurred while testing URL {current_url}: {e}")
            continue  # Optional: Decide whether to continue or break the loop

        # Extract more URLs from the current URL
        extracted_urls = extract_urls(current_url)

        # Filter out external URLs and add to the list of URLs to test
        for extracted_url in extracted_urls:
            full_url = urljoin(base_url, extracted_url)
            if full_url not in tested_urls and is_valid_url(full_url, base_url):
                urls_to_test.add(full_url)  # Add to set to prevent duplicates

    # optionally save all tested URLs to a JSON file
    #helpers.extracted_urls_to_json(list(tested_urls), output_filename)
    logging.info(f"Finished URL extraction and testing from: {url}")
    # Return the results
    return {"tested_urls": list(tested_urls)}

if __name__ == "__main__":
    # This block is for testing purposes
    test_url = "https://example.com"
    results = extract_and_test_urls(test_url)
    print(results)