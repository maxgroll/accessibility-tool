# web_accessibility_checker.py

import validators
import logging
import streamlit as st
from typing import Optional, List, Dict

from data.config import setup_directories, setup_logging
from util.extract_urls_for_tests import extract_all_urls
from util.accessibility_tester import run_accessibility_tests
from util import is_url_accessible, create_test_directory

setup_directories()
setup_logging()

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

    # Initialize the session state for extracted URLs
    if "extracted_urls" not in st.session_state:
        st.session_state.extracted_urls = set()

    # Button to find all URLs on the given page
    if st.button("Find URLs") or url:
        if not validators.url(url):
            st.error("Please provide a valid URL")
            return
        elif not is_url_accessible(url):
            st.error("The URL is not accessible. Please check the URL and try again.")
            return  # Exit the function early
        
        # Use the extracted URLs from the session state if available
        if st.session_state.extracted_urls:
            extracted_urls = st.session_state.extracted_urls
            st.success("Using previously extracted URLs.")
        else:
            try:
                extracted_urls = set(extract_all_urls(url))
                st.session_state.extracted_urls = extracted_urls  # Save to session state
                st.success("Accessible URLs found. Please select the URLs to test.")
            except Exception as e:
                st.error("An unexpected error occurred. Please try again later.")
                logging.error(f"Unexpected error during URL extraction: {e}")
                return
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
                

if __name__ == "__main__":
    main()
