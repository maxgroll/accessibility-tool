# new_tool.py

import logging
import os
import validators
import streamlit as st
from util.url_tester import extract_and_test_urls
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

def main():
    """
    Main function to run the Streamlit app interface for the Web Accessibility Checker.

    This function sets up the Streamlit interface, takes user input for the URL to be tested,
    validates the URL, checks its accessibility, and then runs accessibility tests if the URL is valid and accessible.
    Results are displayed in the Streamlit interface.
    """

    st.title("Web Accessibility Checker")

    # Setup a placeholder for user feedback
    feedback = st.empty()

    # Get user input
    url = st.text_input("Enter the URL of the website to check")

    # Check accessibility and extract URLs when the user clicks the 
    # "Check Accessibility" button or enters a URL
    if st.button("Check Accessibility") or url:
        if not validators.url(url):
            feedback.error("Please provide a valid URL")
            return  # Exit the function early

        feedback.info("Checking URL accessibility...")
        if not is_url_accessible(url):
            feedback.error("The URL is not accessible. Please check the URL and try again.")
            return  # Exit the function early

        feedback.info("URL is accessible. Running accessibility tests...")

        try:
            # Extract and test URLs
            results = extract_and_test_urls(url)
            if results:
                feedback.success("Accessibility check completed")
                st.json(results)
            else:
                feedback.error("An error occurred while checking the website")
                logging.error("No results were returned from extract_and_test_urls.")
        except Exception as e:
            feedback.error("An unexpected error occurred during the accessibility check. Please try again later.")
            logging.error(f"Unexpected error during accessibility checks: {e}")

if __name__ == "__main__":
    main()
