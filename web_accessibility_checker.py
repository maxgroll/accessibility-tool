# web_accessibility_checker.py

import streamlit as st

from util.helper_functions import HelperFunctions
from util.sitemap_parser import SitemapParser
from util.ui_components import UIComponents
from util.website_crawler import WebsiteCrawler

# Setup logging and directories
HelperFunctions.initialize_logging_and_directories()

def main() -> None:
    """
    Main function to run the Streamlit app interface for the Web Accessibility Checker.

    This function sets up the Streamlit interface, takes user input for the URL to be tested,
    validates the URL, checks its accessibility, and then runs accessibility tests on each URL
    that is valid and accessible.
    """
    # Initialize helper functions and UI components
    ui = UIComponents()
    helper = HelperFunctions()

    # Check credentials
    if not helper.check_credentials():
        return

    # Display header
    ui.setup_header()

    # Custom CSS styling
    ui.setup_custom_css()

    # Initialize session state
    helper.initialize_session_state()

    # Define layout for crawling and test choice
    col1, col2 = st.columns(2)

    # Containers for forms and test choices
    with col1:
        find_urls_container = st.container()
    with col2:
        test_choice_container = st.container()

    # Build the forms within the defined containers
    with find_urls_container:
        ui.build_find_urls_form(helper, WebsiteCrawler, SitemapParser)
        
    with test_choice_container:
        ui.handle_test_choice()

    # Display results if tests have been performed
    if st.session_state.show_tests:
        base_results_directory = 'data/accessibility_results'
        latest_results_directory = helper.get_latest_results_directory(base_results_directory)
        
        st.subheader('a11y Test Results')
        # Define the layout for results display
        col1, col2 = st.columns(2)
        
        with col1:
            results_container = st.container()
        with col2:
            gauge_container = st.container()

        # Build the results display within the defined containers
        with results_container:
            ui.build_results_display(latest_results_directory)
        with gauge_container:
            ui.build_gauge_and_download_display(latest_results_directory)
        
        if not st.session_state.test_choice == 'Select specific URLs':
            st.session_state.test_choice = False

if __name__ == "__main__":
    main()