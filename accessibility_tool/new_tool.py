# new_tool.py

import validators
import streamlit as st
from util.url_tester import extract_and_test_urls

def main():
    st.title("Web Accessibility Checker")

    # Get user input
    url = st.text_input("Enter the URL of the website to check")

    # Check accessibility and extract URLs when the user clicks the 
    # "Check Accessibility" button or enters a URL
    if st.button("Check Accessibility") or url:
        if url:
            if not validators.url(url):
                st.error("Please provide a valid URL")
            else:
                # Hier wird nun die Funktion aus dem Modul utils.url_tester aufgerufen
                results = extract_and_test_urls(url)
                if results:
                    st.success("Accessibility check completed")
                    st.json(results)
                else:
                    st.error("An error occurred while checking the website")

if __name__ == "__main__":
    main()
