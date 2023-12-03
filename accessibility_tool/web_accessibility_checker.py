# web_accessibility_checker.py

import validators
import logging
import streamlit as st
from urllib.parse import urlparse
from typing import List

from data.config import setup_directories, setup_logging
from util import is_url_accessible
from util import AccessibilityTester, WebsiteCrawler, SitemapParser


# Setup logging and directories
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

    # Get user input: URL and crawl_depth
    with st.form(key='find_urls_form', clear_on_submit=True):
        url = st.text_input(label='Enter the URL of the website to check')
        # Add a number input for crawl depth
        crawl_depth = st.number_input('Set Crawl Depth', min_value=1, value=3)  # default value is 3
        find_urls_button = st.form_submit_button(label='Find URLs')

    # Initialize the session state for extracted URLs
    if "extracted_urls" not in st.session_state:
        st.session_state.extracted_urls = set()

    # Initialize session state for test choice and choice made
    if "test_choice" not in st.session_state:
        st.session_state.test_choice = "Test only homepage"
    if "choice_made" not in st.session_state:
        st.session_state.choice_made = False

    # Check if Button or enter key was clicked and validate URL
    if find_urls_button or url:
        # Check if provided URL is in session state and reset
        if "previous_url" not in st.session_state or st.session_state.previous_url != url:
            st.session_state.extracted_urls = set()  # Reset the URLs if a new URL is entered
            st.session_state.previous_url = url  # Store the new URL
            # Reset the choice made state to force user to make a choice again
            st.session_state.choice_made = False
            st.session_state.test_choice = None

        # Validation of provided URL
        if not validators.url(url):
            st.error("Please provide a valid URL")
            return # Exit the function early
        elif not is_url_accessible(url):
            st.error("The URL is not accessible. Please check the URL and try again.")
            return  # Exit the function early
        #set the base-url
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/"
        # Use the extracted URLs from the session state if available
        if st.session_state.extracted_urls:
            extracted_urls = st.session_state.extracted_urls
            st.info(f"Using extracted URLs from {base_url}", icon="ℹ️")
        else:
            try:
                # Instantiate sitemap parser
                sitemap_parser = SitemapParser(base_url)
                # Instantiate crawler
                crawler = WebsiteCrawler(base_url)
                logging.info(f"Checking for sitemap on {base_url}")
                # Try to use the sitemap if it exists
                if sitemap_parser.has_sitemap():
                    logging.info(f"Sitemap found on {base_url}: Extracting Urls for Accessibility Tests")
                    st.info("Sitemap found. Extracting Urls for Accessibility Tests")
                    # TODO with st.spinner("Extracting URLs from sitemap"):
                    extracted_urls = sitemap_parser.get_sitemap_urls()
                    if not extracted_urls:  # If sitemap parsing returns an empty set
                        # If the sitemap can not be parsed fallback to crawl
                        with st.spinner("Sitemap index found but could not be parsed. Crawling for URLs"):
                            extracted_urls = crawler.crawl_urls_to_test(base_url, crawl_depth)
                else:
                    # No sitemap found, start crawling for URLs
                    logging.info(f"No sitemap found on {url}: Crawling for URLs started")
                    with st.spinner("No sitemap found. Crawling for URLs"):
                        extracted_urls = crawler.crawl_urls_to_test(base_url, crawl_depth)
                # Add extracted URLs to session state
                st.session_state.extracted_urls = extracted_urls
                st.success(f"{len(extracted_urls)} Accessible URLs found on {base_url}. Please select the URLs to test.")
            except Exception as e:
                st.error("An unexpected error occurred. Please try again later.")
                logging.error(f"Unexpected error during URL extraction: {e}")
                return
        # Radio button for user to chosse test type
        test_form = st.form(key='test_choice_form', clear_on_submit=True)
        #with st.form(key='test_choice_form', clear_on_submit=True):
        with test_form:
            test_choice = st.radio(
            f"Select the URLs to test from {len(extracted_urls)} URLs:",
            ('Test only homepage', 'Test all URLs', 'Select specific URLs'),
            index=None, # Default selection is 'None'
        )
            choice_made = st.form_submit_button(label='Confirm Choice')
            
        # Update session state based on user's choice
        if choice_made:
            st.session_state.choice_made = True
            st.session_state.test_choice = test_choice

        # Logic based on user's choice
        if st.session_state.choice_made:
            tester = AccessibilityTester()
            if st.session_state.test_choice == 'Test all URLs':
                # Logic to test all URLs
                logging.info(f"Starting accessibility Tests from: {base_url}")
                with st.spinner("Performing accessibility tests"):
                    if extracted_urls:
                        results = tester.test_urls(extracted_urls)
                    
                        if results:
                            st.success("Accessibility tests completed")
                            logging.info(f"Finished accessibility Tests from: {base_url} \n {len(extracted_urls)} URLs tested: {extracted_urls}")
                        else:
                            st.error("An error occurred while checking the selected URLs.")
                    else:
                        st.error("No URLs selected for testing.")

            if st.session_state.test_choice == 'Test only homepage':
                    # Logic to test only the homepage
                    urls = set()
                    urls.add(base_url)
                    logging.info(f"Starting accessibility Tests from: {base_url}")
                    with st.spinner("Performing accessibility tests on the homepage"):
                        if urls:
                            results = tester.test_urls(urls)

                        if results:
                            st.success(f"Accessibility test for the homepage {base_url} completed")
                            logging.info(f"Finished accessibility Test from: {base_url}")
                        else:
                            st.error("An error occurred while checking the homepage.")

        if st.session_state.extracted_urls and st.session_state.choice_made and st.session_state.test_choice == 'Select specific URLs':
            # Show multiselect widget for selecting specific URLs
            with st.form(key='run_tests_form', clear_on_submit=True):
                selected_urls: List[str] = st.multiselect("Select URLs to test", options=list(extracted_urls), default=None)
                run_tests_button = st.form_submit_button(label='Run Accessibility Tests')

            # Button to run tests on selected URLs
            if run_tests_button:
                logging.info(f"Starting accessibility Tests from: {base_url}")
                with st.spinner("Performing accessibility tests"):
                    if selected_urls:
                        results = tester.test_urls(selected_urls)
                    
                        if results:
                            st.success("Accessibility tests completed")
                            logging.info(f"Finished accessibility Tests from: {base_url} \n {len(selected_urls)} URLs tested: {selected_urls}")
                        else:
                            st.error("An error occurred while checking the selected URLs.")
                    else:
                        st.error("No URLs selected for testing.")
                

if __name__ == "__main__":
    main()
