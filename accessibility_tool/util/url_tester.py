# url_tester.py

#import validators
from urllib.parse import urljoin
from .accessibility_tester import run_accessibility_tests
from .url_extractor import extract_urls
from .helpers import is_valid_url

import os


def extract_and_test_urls(url, output_filename="extracted_urls.json"):
    """
    Extracts URLs from a given base URL and performs accessibility tests on them.
    
    Args:
        url (str): The base URL to extract links from and test.
        output_filename (str): The filename where to save the extracted URLs.
        
    Returns:
        dict: A dictionary with the test results.
    """
    # Initialize set for storing tested URLs and list for URLs to test
    tested_urls = set()
    urls_to_test = {url}  # Change to a set to prevent duplicates

    # Determine the base URL for resolving relative links
    base_url = urljoin(url, '/')

    ############
    general_test_dir = 'accessibility_results'
    os.makedirs(general_test_dir, exist_ok=True)

    # Schritt 2: Erstellen des spezifischen Domainordners
    #base_url = "https://otros.eu"
    #domain_dir_name = url_to_dir_name(base_url)
    #domain_test_dir = os.path.join(general_test_dir, domain_dir_name)
    #os.makedirs(domain_test_dir, exist_ok=True)
    #print(domain_test_dir)
    ############

    # Loop through URLs to test
    while urls_to_test:
        current_url = urls_to_test.pop()

        # Skip testing for certain conditions
        if current_url in tested_urls or not is_valid_url(current_url, base_url):
            continue

        # Add the current URL to the set of tested URLs
        try:
            run_accessibility_tests(current_url)
            tested_urls.add(current_url)
        except Exception as e:
            print(f"Ein Fehler ist beim Testen der URL {current_url} aufgetreten: {e}")

        # Extract more URLs from the current URL
        extracted_urls = extract_urls(current_url)

        # Filter out external URLs and add to the list of URLs to test
        for extracted_url in extracted_urls:
            full_url = urljoin(base_url, extracted_url)
            if full_url not in tested_urls and is_valid_url(full_url, base_url):
                urls_to_test.add(full_url)  # Add to set to prevent duplicates

    # Save all tested URLs to a JSON file
    #extracted_urls_to_json(list(tested_urls), output_filename)

    # Return the results
    return {"tested_urls": list(tested_urls)}

if __name__ == "__main__":
    # This block is for testing purposes
    test_url = "https://example.com"
    results = extract_and_test_urls(test_url)
    print(results)