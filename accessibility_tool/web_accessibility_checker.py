# web_accessibility_checker.py

import validators
import logging
import streamlit as st
from typing import Optional, List, Dict
from urllib.parse import urlparse

from data.config import setup_directories, setup_logging
from util.accessibility_tester import run_accessibility_tests
from util import is_url_accessible, create_test_directory

from util.website_crawler import WebsiteCrawler
from util.sitemap_parser import SitemapParser

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
    with st.form(key='find_urls_form'):
        url = st.text_input(label='Enter the URL of the website to check')
        # Add a number input for crawl depth
        crawl_depth = st.number_input('Set Crawl Depth', min_value=1, value=3)  # default value is 3
        find_urls_button = st.form_submit_button(label='Find URLs')

    # Initialize the session state for extracted URLs
    if "extracted_urls" not in st.session_state:
        st.session_state.extracted_urls = set()

    ### nuevo
    if "test_choice" not in st.session_state:
        st.session_state.test_choice = "Test all URLs"
    if "choice_made" not in st.session_state:
        st.session_state.choice_made = False

    # Check if Button or enter key was clicked and validate URL
    if find_urls_button or url:
        #logging.info(f"find_urls Button klicked for: {url}")
        # Check if provided URL is in session state and reset
        if "previous_url" not in st.session_state or st.session_state.previous_url != url:
            st.session_state.extracted_urls = set()  # Reset the URLs if a new URL is entered
            st.session_state.previous_url = url  # Store the new URL
        # Reset the choice made state to force user to make a choice again
        st.session_state.choice_made = False

        # Validation of provided URL
        if not validators.url(url):
            st.error("Please provide a valid URL")
            return
        elif not is_url_accessible(url):
            st.error("The URL is not accessible. Please check the URL and try again.")
            return  # Exit the function early
        
        # Use the extracted URLs from the session state if available
        if st.session_state.extracted_urls:
            extracted_urls = st.session_state.extracted_urls
            #st.success("Using previously extracted URLs.")
        else:
            try:
                logging.info(f"Checking for sitemap on {url}")
                # Try to use the sitemap if it exists
                sitemap_parser = SitemapParser(url)
                if sitemap_parser.has_sitemap():
                    logging.info(f"Sitemap found on {url}: Extracting Urls for Accessibility Tests")
                    st.info("Sitemap found. Extracting Urls for Accessibility Tests")
                    # TODO with st.spinner("Extracting URLs from sitemap"):
                    extracted_urls = sitemap_parser.get_sitemap_urls()
                    if not extracted_urls:  # If sitemap parsing returns an empty set
                        #logging.info(f"Sitemap index found but could not be parsed for {url}. Falling back to crawling.")
                        with st.spinner("Sitemap index found but could not be parsed. Crawling for URLs"):
                            crawler = WebsiteCrawler(url)
                            #crawler.crawl(url)
                            crawler.crawl(url, max_depth=crawl_depth)  # Here you pass the crawl_depth
                            extracted_urls = crawler.get_crawled_urls()
                            logging.info(f"Crawling {url} finished")
                else:
                    # No sitemap found, start crawling for URLs
                    logging.info(f"No sitemap found on {url}: Crawling for URLs started")
                    #st.info("No sitemap found. Crawling for URLs started")
                    with st.spinner("No sitemap found. Crawling for URLs"):
                        crawler = WebsiteCrawler(url)
                        #crawler.crawl(url)
                        crawler.crawl(url, max_depth=crawl_depth)  # Here you pass the crawl_depth
                        extracted_urls = crawler.get_crawled_urls()
                        logging.info(f"Crawling {url} finished")

                # Add extracted URLs to session state
                st.session_state.extracted_urls = extracted_urls
                st.success("Accessible URLs found. Please select the URLs to test.")
            except Exception as e:
                st.error("An unexpected error occurred. Please try again later.")
                logging.error(f"Unexpected error during URL extraction: {e}")
                return
        st.empty()

#######
        with st.form(key='test_choice_form'):
            test_choice = st.radio(
                "Select the URLs to test:",
                ('Test all URLs', 'Test only homepage', 'Select specific URLs'),
                index=0  # Standardauswahl ist 'Test all URLs'
            )
            choice_made = st.form_submit_button(label='Confirm Choice')

        if choice_made:
            st.session_state.choice_made = True
            st.session_state.test_choice = test_choice

        # Logic based on user's choice (execute only if choice has been made)
        if st.session_state.choice_made:
            if st.session_state.test_choice == 'Test all URLs':
                # Logic to test all URLs
                logging.info(f"Starting accessibility Tests from: {url}")
                with st.spinner("Performing accessibility tests"):
                    if extracted_urls:
                        results: Optional[Dict] = {}
                    # Loop through the list of selected URLs, create a directory for each URL's test results, and run accessibility tests
                        for single_url in extracted_urls:
                            test_directory = create_test_directory(single_url)
                            results[single_url] = run_accessibility_tests(single_url, test_directory)

                        if results:
                            st.success("Accessibility tests completed")
                            logging.info(f"Finished accessibility Tests from: {url} \n {len(extracted_urls)} URLs tested: {extracted_urls}")
                        else:
                            st.error("An error occurred while checking the selected URLs.")
                    else:
                        st.error("No URLs selected for testing.")
            
            elif st.session_state.test_choice == 'Test only homepage':
                # Logic to test only the homepage
                logging.info(f"Starting accessibility Tests from: {url}")
                parsed_url = urlparse(url)
                homepage_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                with st.spinner("Performing accessibility tests on the homepage"):
                    results: Optional[Dict] = {}
                    test_directory = create_test_directory(homepage_url)
                    results[homepage_url] = run_accessibility_tests(homepage_url, test_directory)
        
                    if results:
                        st.success(f"Accessibility test for the homepage {homepage_url} completed")
                        logging.info(f"Finished accessibility Test from: {homepage_url}")
                    else:
                        st.error("An error occurred while checking the homepage.")
               
            elif st.session_state.test_choice == 'Select specific URLs':
                # Form to run tests on selected URLs
                with st.form(key='run_tests_form'):
                    # Display URLs as a multiselect widget
                    selected_urls: List[str] = st.multiselect("Select URLs to test", options=list(extracted_urls), default=list(extracted_urls))
            
                    # Button to run tests on selected URLs
                    run_tests_button = st.form_submit_button(label='Run Accessibility Tests')

                    # if run tests button is clicked
                    if run_tests_button:
                        logging.info(f"Starting accessibility Tests from: {url}")
                        with st.spinner("Performing accessibility tests"):
                            if selected_urls:
                                results: Optional[Dict] = {}
                                # Loop through the list of selected URLs, create a directory for each URL's test results, and run accessibility tests
                                for single_url in selected_urls:
                                    test_directory = create_test_directory(single_url)
                                    results[single_url] = run_accessibility_tests(single_url, test_directory)

                                if results:
                                    st.success("Accessibility tests completed")
                                    logging.info(f"Finished accessibility Tests from: {url} \n {len(selected_urls)} URLs tested: {selected_urls}")
                                else:
                                    st.error("An error occurred while checking the selected URLs.")
                            else:
                                st.error("No URLs selected for testing.")
                

if __name__ == "__main__":
    main()
