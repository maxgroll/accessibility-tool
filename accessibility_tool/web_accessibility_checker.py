# web_accessibility_checker.py

import validators
import logging
import os
import streamlit as st
from typing import Optional, List, Dict
from util.extractor_test import extract_all_urls
from util.helpers import create_test_directory
from util.accessibility_tester import run_accessibility_tests
from util.helpers import is_url_accessible

# configuration of logging system
log_directory = "logs"
os.makedirs(log_directory, exist_ok=True)  # Erstellt den Ordner, falls er noch nicht existiert

log_file_path = os.path.join(log_directory, "debug.log")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[
                        logging.FileHandler(log_file_path),  # Fehlermeldungen werden in debug.log gespeichert.
                        logging.StreamHandler()  # Fehlermeldungen werden auch in der Konsole ausgegeben.
                    ])

# Set up the general directory to store accessibility test results
general_test_dir = 'accessibility_results'
os.makedirs(general_test_dir, exist_ok=True)

def main():
    """
    Main function to run the Streamlit app interface for the Web Accessibility Checker.

    This function sets up the Streamlit interface, takes user input for the URL to be tested,
    validates the URL, checks its accessibility, and then runs accessibility tests on each if the URLs 
    that is valid and accessible.
    """
    st.title("Web Accessibility Checker")

    # Get user input
    url = st.text_input("Enter the URL of the website to check")

    # Button to find all URLs on the given page
    if st.button("Find URLs") or url:
        if not validators.url(url):
            st.error("Please provide a valid URL")
        elif not is_url_accessible(url):
            st.error("The URL is not accessible. Please check the URL and try again.")
            return  # Exit the function early
        else:
            try:
                extracted_urls = set(extract_all_urls(url))
                if extracted_urls:
                    st.success("Accessible URLs found. Please select the URLs to test.")
                    # Display URLs as a multiselect widget
                    selected_urls: List[str] = st.multiselect("Select URLs to test", options=list(extracted_urls), default=list(extracted_urls))
                    # Button to run tests on selected URLs
                    if st.button("Run Accessibility Tests"):
                        logging.info(f"Starting accessibility Tests from: {url}")
                        if selected_urls:
                            results: Optional[Dict] = {}
                            # Loop through the list of selected URLs, create a directory for each URL's test results, and run accessibility tests
                            for single_url in selected_urls:
                                test_directory = create_test_directory(single_url)
                                results[single_url] = run_accessibility_tests(single_url, test_directory)

                            if results:
                                st.success("Accessibility tests completed")
                                logging.info(f"Finished accessibility Tests from: {url} \n {len(selected_urls)} URLs tested: {selected_urls}")
                                
                                #st.json(results)
                            else:
                                st.error("An error occurred while checking the selected URLs.")
                        else:
                            st.error("No URLs selected for testing.")
                else:
                    st.error("No accessible URLs found on the page.")
            except Exception as e:
                st.error("An unexpected error occurred. Please try again later.")
                logging.error(f"Unexpected error during URL extraction: {e}")


if __name__ == "__main__":
    main()
