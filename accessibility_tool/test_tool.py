# web_accessibility_checker.py

import validators
import logging
import streamlit as st
from urllib.parse import urlparse
from typing import List
from PIL import Image

from data.config import setup_directories, setup_logging
from util import is_url_accessible
from util import AccessibilityTester, WebsiteCrawler, SitemapParser

from util.accessibility_report_viewer import AccessibilityReportViewer
from util.helpers import get_latest_results_directory
import os

def display_results_ui(latest_results_directory):
    st.subheader('Accessibility Test Results', divider='grey')

    # Layout for the selectboxes
    col1, col2 = st.columns(2)

    with col1:
    # Get all JSON result files in the latest results directory
        json_result_files = [f for f in os.listdir(latest_results_directory) if f.endswith('.json')]
        csv_result_files = [f for f in os.listdir(latest_results_directory) if f.endswith('.csv')]

        # Display a selectbox for the user to choose which result file to view
        selected_result_file = st.selectbox('Select a test result to view', json_result_files)

    # Display the selected test result
        if selected_result_file:
            result_path = os.path.join(latest_results_directory, selected_result_file)
            report_viewer = AccessibilityReportViewer(result_path)
        
        # Calculate and display the accessibility score
            score = report_viewer.calculate_accessibility_score()
            st.metric(label="Accessibility Score", value=f"{score}%")

            violations_df = report_viewer.create_violations_dataframe()
            st.dataframe(violations_df)

    with col2:
        # Display a selectbox for the user to choose which result file to download
        st.write("Download Test Results")
        download_file = st.selectbox('Select a test result to download', json_result_files + csv_result_files)
        if download_file:
            # Provide the download button for the selected file
            file_path = os.path.join(latest_results_directory, download_file)
            with open(file_path, "rb") as fp:
                st.download_button(
                    label="Download File",
                    data=fp,
                    file_name=download_file,
                    mime="application/octet-stream"
                )


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
    header_container = st.container()
    with header_container:
        logo = Image.open("static/digitalagenten_Logo_quer-2.png")
        st.image(logo, width=300)
        st.header("Web Accessibility Checker", divider='grey')

    st.markdown("""
        <style>
       
        .stHeadingContainer {
            text-align: center; 
            color: black;     
        }
                
       .block-container {
            max-width: 100rem;
        }
        
             
        .block-container [data-testid="column"] {
            border: 2px solid rgba(49, 51, 63, 0.3);
            border-radius: 15px;
            padding: 10px;
            box-shadow: 1px 1px 1px rgba(49, 51, 63, 0.1);
        }
        
        /* This creates a border around the Streamlit components 
        .stTextInput, .stSelectbox, .stMultiselect{
            border: 2px solid blue;
            border-radius: 5px;
            padding: 5px 10px;
        }*/
        </style>
        """, unsafe_allow_html=True)

   
    col1, col2 = st.columns(2)

    with col1:
        find_urls_container = st.container()
        
    with col2:
        test_choice_container = st.container()
        with test_choice_container:
            test_choice_form = st.form(key='test_choice_form', clear_on_submit=True)
            with test_choice_form:
                st.subheader("Choose Test Type", divider="grey")
                tests_placeholder = st.empty()
                choice_made = st.form_submit_button(label='Confirm Choice')
    
        run_tests_container = st.container()
        with run_tests_container:
            run_tests_form = st.form(key='run_tests_form')
            with run_tests_form:
                st.subheader("Select URLs to test", divider="grey")
                run_placeholder = st.empty()
                run_tests_button = st.form_submit_button(label='Run Accessibility Tests')

    with find_urls_container:
        # Get user input: URL and crawl_depth
        with st.form(key='find_urls_form'):
            st.subheader("Find URLs", divider="grey")  # Add a title
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

         # Initialize the show_tests state to False
        if 'show_tests' not in st.session_state:
                st.session_state.show_tests = False

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
            base_path = parsed_url.path.rstrip('/')  # Remove trailing slash for consistency
            if base_path:
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{base_path}/"
            else:
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
            with test_choice_container:
                with test_choice_form:
                    test_choice = tests_placeholder.radio(
                    f"Select the URLs to test from {len(extracted_urls)} URLs:",
                    ('Test only homepage', 'Test all URLs', 'Select specific URLs'),
                    index=None, # Default selection is 'None'
                )
            
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
            
                        st.session_state.show_tests = True


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
                       
                        st.session_state.show_tests = True

        with run_tests_container:
            #if st.session_state.test_choice == 'Select specific URLs':
        #####
                #st.session_state.choice_made = True
            if st.session_state.extracted_urls and st.session_state.choice_made and st.session_state.test_choice == 'Select specific URLs':
            # Show multiselect widget for selecting specific URLs
                with run_tests_form:
                    selected_urls: List[str] = run_placeholder.multiselect("Select URLs to test", options=list(extracted_urls), default=None, placeholder="Choose URLs To Test")
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
                
                    st.session_state.show_tests = True
                    

    # After all tests have been run and results are ready to be displayed:
    if st.session_state.show_tests:
        base_results_directory = 'data/accessibility_results'  # Update with actual path
        latest_results_directory = get_latest_results_directory(base_results_directory)
        display_results_ui(latest_results_directory)
        # TODO if commented out this test runs even if i have tested just the homepage
        # but with rerun if i interact with anything in the views panel
        # if take it in, there are no reruns, but the choice for selecting urls
        # does not work 
        st.session_state.test_choice = 'Select specific URLs'
        ###
        #st.session_state.choice_made = False
        
                

if __name__ == "__main__":
    main()
