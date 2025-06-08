# helper_functions.py
import json
import os
import logging
import validators
import streamlit as st
import requests
from urllib.parse import urlparse, urlunparse
from urllib.robotparser import RobotFileParser
from datetime import datetime
from typing import Optional
from config import setup_directories, setup_logging, FULL_ACCESSIBILITY_RESULTS_DIRECTORY



class HelperFunctions:
    """
    A class containing helper functions for the Web Accessibility Checker.

    This class includes methods for logging and directory setup, session state initialization,
    URL validation, sitemap checking, and results directory management.
    """

    @staticmethod
    def initialize_logging_and_directories() -> None:
        """
        Initializes logging and directory setup for the application.
        """
        setup_directories()
        setup_logging()

    @staticmethod
    def check_credentials() -> bool:
        """
        Checks username and password credentials for access.

        Returns:
            bool: True if credentials are correct, False otherwise.
        """
        if "credentials_correct" not in st.session_state:
            st.session_state.credentials_correct = False

        if not st.session_state.credentials_correct:
            with st.form(key='login_form'):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                login_button = st.form_submit_button("Login")

            if login_button:
                if (username == st.secrets["credentials"]["username"] and
                    password == st.secrets["credentials"]["password"]):
                    st.session_state.credentials_correct = True
                    st.rerun()  # Immediately rerun the app to update the UI
                else:
                    st.session_state.credentials_correct = False
                    st.error("😕 Username or password incorrect")

        return st.session_state.credentials_correct

    @staticmethod
    def extract_domain_and_page_from_json(json_file_path: str) -> str:
        """
        Extracts domain and page information from a JSON file containing URL data.

        Args:
            json_file_path (str): Path to the JSON file.

        Returns:
            str: A formatted string of the domain and page path.
        """
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            url = data.get('url', '')
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            path = parsed_url.path.rstrip('/').lstrip('/')
            return f"{domain}/{path}" if path else domain

    @staticmethod
    def initialize_session_state() -> None:
        """
        Initializes the session state variables for the Streamlit app.
        """
        if "extracted_urls" not in st.session_state:
            st.session_state.extracted_urls = set()
        if "test_choice" not in st.session_state:
            st.session_state.test_choice = "Test only homepage"
        if "choice_made" not in st.session_state:
            st.session_state.choice_made = False
        if 'show_tests' not in st.session_state:
            st.session_state.show_tests = False
        if 'previous_url' not in st.session_state:
            st.session_state.previous_url = ""
        if 'axe_version' not in st.session_state:
            st.session_state.axe_version = None
        if 'download_initiated' not in st.session_state:
            st.session_state.download_initiated = False
       
    @staticmethod
    def handle_url_extraction(url: str, crawl_depth: int, WebsiteCrawler, SitemapParser) -> None:
        """
        Handles the URL extraction based on the user's choice.

        Args:
            url (str): The URL to extract from.
            crawl_depth (int): The depth to crawl if crawling.
            WebsiteCrawler: The website crawler class.
            SitemapParser: The sitemap parser class.

        Returns:
            None
        """
        from util.accessibility_tester import AccessibilityTester

        if "previous_url" not in st.session_state or st.session_state.previous_url != url:
            st.session_state.extracted_urls = set()
            st.session_state.previous_url = url
            st.session_state.choice_made = False
            st.session_state.test_choice = None

        if not validators.url(url):
            st.error("Please provide a valid URL")
            return
        elif not HelperFunctions.is_url_accessible(url):
            st.error("The URL is not accessible. Please check the URL and try again.")
            return

        if st.session_state.extraction_method == 'Test only entered URL':
            st.session_state.extracted_urls = {url}
            st.session_state.previous_url = url
            st.session_state.extracted_urls_valid = True
            st.session_state.sitemap_exists = False

            # Immediately send URL for testing
            if 'tester' not in st.session_state:
                st.session_state.tester = AccessibilityTester(st.session_state.axe_version)
            st.session_state.show_tests = True
            st.session_state.choice_made = True
            st.session_state.test_choice = 'Test only homepage'
        elif st.session_state.extraction_method == 'Use Sitemap':
            sitemap_parser = SitemapParser(url)
            if sitemap_parser.has_sitemap():
                logging.info(f"Sitemap found on {url}: Extracting URLs for Accessibility Tests")
                st.info("Sitemap found. Extracting URLs for Accessibility Tests")
                extracted_urls = sitemap_parser.get_sitemap_urls()
                logging.info(f"Extracted {len(extracted_urls)} URLs from {url}")
                if not extracted_urls:
                    with st.spinner("Sitemap index found but could not be parsed. Crawling for URLs"):
                        crawler = WebsiteCrawler(url)
                        extracted_urls = crawler.crawl_urls_to_test(url, crawl_depth)
                if extracted_urls:
                    st.session_state.extracted_urls = extracted_urls
                    st.session_state.previous_url = url
                    st.session_state.extracted_urls_valid = True
                    st.success(f"Extracted {len(extracted_urls)} URLs from the sitemap.")
                else:
                    st.error("No URLs extracted from the sitemap. Please choose to crawl the website.")
            else:
                st.error("No sitemap found. Please choose Crawl Website to extract URLs.")
        elif st.session_state.extraction_method == 'Crawl Website':
            crawler = WebsiteCrawler(url)
            with st.spinner("Crawling for URLs"):
                extracted_urls = crawler.crawl_urls_to_test(url, crawl_depth)
            if extracted_urls:
                st.session_state.extracted_urls = extracted_urls
                st.session_state.previous_url = url
                st.session_state.extracted_urls_valid = True
                st.success(f"Crawling finished. Extracted {len(extracted_urls)} URLs.")
            else:
                st.error("No URLs extracted. Please check the website URL or increase the crawl depth.")
        
    @staticmethod
    def handle_url_extraction_(url: str, crawl_depth: int, website_crawler_cls, sitemap_parser_cls) -> None:
        """
        Handles the URL extraction logic for the Streamlit app.

        Args:
            url (str): The URL to be processed.
            crawl_depth (int): The depth to crawl for URLs.
            website_crawler_cls: The class to use for website crawling.
            sitemap_parser_cls: The class to use for sitemap parsing.
        """
        if "previous_url" not in st.session_state or st.session_state.previous_url != url:
            st.session_state.extracted_urls = set()
            st.session_state.previous_url = url
            st.session_state.choice_made = False
            st.session_state.test_choice = None

        if not validators.url(url):
            st.error("Please provide a valid URL")
            return
        elif not HelperFunctions.is_url_accessible(url):
            st.error("The URL is not accessible. Please check the URL and try again.")
            return

        parsed_url = urlparse(url)
        base_path = parsed_url.path.rstrip('/')
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{base_path}/" if base_path else f"{parsed_url.scheme}://{parsed_url.netloc}/"

        #TODO implement this but with the choice of using extracted urls or crawl anew
        #if st.session_state.extracted_urls:
            #extracted_urls = st.session_state.extracted_urls
            #st.info(f"Using extracted URLs from {base_url}", icon="ℹ️")
        #else:
        try:
            sitemap_parser = sitemap_parser_cls(base_url)
            crawler = website_crawler_cls(base_url)
            logging.info(f"Checking for sitemap on {base_url}")

            if st.session_state.use_sitemap == 'Use Sitemap' and sitemap_parser.has_sitemap():
                logging.info(f"Sitemap found on {base_url}: Extracting URLs for Accessibility Tests")
                st.info("Sitemap found. Extracting URLs for Accessibility Tests")
                extracted_urls = sitemap_parser.get_sitemap_urls()
                logging.info(f"Extracted {len(extracted_urls)} URLs from {base_url}")
                if not extracted_urls:
                    with st.spinner("Sitemap index found but could not be parsed. Crawling for URLs"):
                        extracted_urls = crawler.crawl_urls_to_test(base_url, crawl_depth)
            else:
                logging.info(f"No sitemap found or user chose to crawl: Crawling for URLs started")
                with st.spinner("Crawling for URLs"):
                    extracted_urls = crawler.crawl_urls_to_test(base_url, crawl_depth)

            st.session_state.extracted_urls = extracted_urls
            st.success(f"{len(extracted_urls)} Accessible URLs found on {base_url}. Please select the URLs to test.")
        except Exception as e:
            st.error("An unexpected error occurred. Please try again later.")
            logging.error(f"Unexpected error during URL extraction: {e}")
            return

    ## TODO use this methods to check for sitemap to display that a siemap is present or not on ui
    @staticmethod
    def check_sitemap(url: str, sitemap_parser_cls) -> bool: #not being used at the moment
        """
        Check if the given URL has a sitemap.

        Args:
            url (str): The URL to check.
            sitemap_parser_cls: The class to use for sitemap parsing.

        Returns:
            bool: True if the URL has a sitemap, False otherwise.
        """
        parsed_url = urlparse(url)
        base_path = parsed_url.path.rstrip('/')
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{base_path}/" if base_path else f"{parsed_url.scheme}://{parsed_url.netloc}/"
        sitemap_parser = sitemap_parser_cls(base_url)
        return sitemap_parser.has_sitemap()

    @staticmethod
    def check_sitemap_and_set_state(url: str, sitemap_parser_cls) -> None: # not being used at the moment
        """
        Checks if the given URL has a sitemap and sets the session state accordingly.

        Args:
            url (str): The URL to check.
            sitemap_parser_cls: The class to use for sitemap parsing.
        """
        if not url:
            return

        parsed_url = urlparse(url)
        base_path = parsed_url.path.rstrip('/')
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{base_path}/" if base_path else f"{parsed_url.scheme}://{parsed_url.netloc}/"
        sitemap_parser = sitemap_parser_cls(base_url)
        st.session_state.sitemap_exists = sitemap_parser.has_sitemap()

    @staticmethod
    #def is_url_accessible(url: str) -> bool:
    def is_url_accessible(url: str, session: Optional[requests.Session] = None) -> bool:
        """
        Check if the given URL is accessible.

        Args:
            url (str): URL to check.

        Returns:
            bool: True if the URL is accessible, False otherwise.
        """
        if not url.startswith(('http://', 'https://')):
            return False
        
#### Add headers to the request to avoid 403 Forbidden errors
        from config.constants import USER_AGENT
        headers = {"User-Agent": USER_AGENT}

        try:
            response = requests.get(url,headers=headers, stream=True, timeout=10)
            response.close()  # Make sure to close the response
            logging.info(f"response: {response}")
            return response.status_code == 200
        except requests.RequestException as e:
            logging.error(f"Failed to access URL {url}: {e}")
            return False

    @staticmethod
    def create_test_directory(url: str) -> str:
        """
        Creates a nested directory structure for test results based on the given URL.
        The structure will be: data/accessibility_tests/domain/timestamp/

        Args:
            url (str): The full URL for which to create the directory structure.

        Returns:
            str: The path to the directory for the specific test-session.
        """
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace('www.', '')

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        directory_path = os.path.join(FULL_ACCESSIBILITY_RESULTS_DIRECTORY, domain, timestamp)
        os.makedirs(directory_path, exist_ok=True)

        return directory_path

    @staticmethod
    def is_valid_url(url: str, base_url: str, session: requests.Session) -> bool:
        """
        Validates a URL based on specific criteria and content type check.

        Args:
            url (str): The URL to validate.
            base_url (str): The base URL of the target website.
            session (requests.Session): The requests session for making HTTP requests.

        Returns:
            bool: True if the URL is valid and points to a webpage, False otherwise.
        """
        parsed_url = urlparse(url)
        cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))

        if not validators.url(cleaned_url):
            logging.debug(f"URL failed validation: {url}")
            return False

        if parsed_url.scheme not in ['http', 'https']:
            logging.debug(f"URL scheme not supported: {url}")
            return False

        if parsed_url.fragment or parsed_url.query:
            logging.debug(f"URL has fragment or query: {url}")
            return False

        ignored_extensions = ['.pdf', '.jpg', 'jpeg', 'webp', '.png', '.svg', '.css', '.js', '.xml']
        if any(parsed_url.path.lower().endswith(ext) for ext in ignored_extensions):
            logging.debug(f"URL has ignored extension: {url}")
            return False

        if not url.startswith(base_url):
            logging.debug(f"URL does not start with base URL: {url}")
            return False

        try:
            response = session.head(cleaned_url, allow_redirects=True, timeout=10)
            if 'text/html' not in response.headers.get('Content-Type', ''):
                logging.debug(f"URL rejected due to content type: {url}")
                return False
        except requests.RequestException as e:
            logging.warning(f"Failed to fetch URL headers for {url}: {e}")
            return False

        return True

    #@staticmethod
    #def can_fetch(url: str, user_agent: str = '*') -> bool:
        """
        Checks if a URL can be fetched based on the website's robots.txt file.

        Args:
            url (str): The URL to check.
            user_agent (str): The user agent of the crawler (default is '*').

        Returns:
            bool: True if fetching the URL is allowed, False otherwise.
        """
       # parsed_url = urlparse(url)
       # robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
       # rp = RobotFileParser()

       # try:
          #  response = requests.get(robots_url)
           # if response.status_code == 200:
              #  rp.parse(response.text.splitlines())
           # else:
               # logging.info(f"No robots.txt found at {robots_url}. Assuming crawling is allowed.")
                #return True
        #except requests.RequestException as e:
            #logging.error(f"Error fetching robots.txt: {e}")
            #return True  # Assume crawling is allowed if there's an error fetching robots.txt

        #allowed = rp.can_fetch(user_agent, url)
        #if not allowed:
           # logging.debug(f"Fetching disallowed by robots.txt: {url} for user-agent {user_agent}")
        #else:
            #logging.debug(f"Fetching allowed by robots.txt: {url} for user-agent {user_agent}")
        #return allowed

    @staticmethod
    def can_fetch(url: str, user_agent: str = '*', session: Optional[requests.Session] = None) -> bool:
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        rp = RobotFileParser()

        try:
            if session:
                response = session.get(robots_url, timeout=10)
            else:
                response = requests.get(robots_url, timeout=10)

            if response.status_code == 200:
                rp.parse(response.text.splitlines())
            else:
                logging.info(f"No robots.txt found at {robots_url}. Assuming crawling is allowed.")
                return True
        except requests.RequestException as e:
            logging.error(f"Error fetching robots.txt: {e}")
            return True

        return rp.can_fetch(user_agent, url)



    @staticmethod
    def get_latest_results_directory(base_results_directory: str) -> Optional[str]:
        """
        Get the latest results directory based on the timestamped directories.

        Args:
            base_results_directory (str): The base directory where results are stored.

        Returns:
            Optional[str]: The path to the latest results directory, or None if not found.
        """
        logging.info(f"Checking for latest results directory in: {base_results_directory}")
        domain_directories = os.listdir(base_results_directory)
        latest_time = datetime.min
        latest_directory = None

        for domain_dir in domain_directories:
            full_domain_path = os.path.join(base_results_directory, domain_dir)
            if os.path.isdir(full_domain_path):  # Ensure it's a directory
                timestamps = [d for d in os.listdir(full_domain_path) if os.path.isdir(os.path.join(full_domain_path, d))]
                for ts in timestamps:
                    try:
                        ts_time = datetime.strptime(ts, "%Y-%m-%d_%H-%M-%S")
                        if ts_time > latest_time:
                            latest_time = ts_time
                            latest_directory = os.path.join(full_domain_path, ts)
                    except ValueError:
                        continue

        return latest_directory
    


    