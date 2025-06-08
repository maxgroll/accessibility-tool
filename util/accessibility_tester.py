# util/accessibility_tester.py

import streamlit as st
import os
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from axe_selenium_python import Axe
from typing import Dict, Optional, Set
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .results_processor import ResultsProcessor
from .helper_functions import HelperFunctions


class AccessibilityTester:
    """
    A class to run accessibility tests on websites using Axe with Selenium.

    This class handles the initialization of the WebDriver, runs Axe accessibility
    tests on specified URLs, and processes the results.

    Attributes:
        chrome_options (Options): Chrome options for Selenium WebDriver.
    """

    def __init__(self, axe_version: str):
        """
        Initializes the AccessibilityTester with Chrome WebDriver options.
        """
        self.test_directory = " "
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-software-rasterizer")
        self.chrome_options.add_argument("--window-size=1920x1080")
        #self.chrome_options.add_argument("--remote-debugging-port=9222")

        #self.chrome_options = Options()
        #self.chrome_options.add_argument("--no-sandbox")
        #self.chrome_options.add_argument("--headless")
        #self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.axe_version = axe_version
        self.driver = self.setup_webdriver()
           
    def setup_webdriver(self) -> webdriver.Chrome:
        """
        Sets up the Chrome WebDriver.

        Returns:
            webdriver.Chrome: The configured Chrome WebDriver instance.
        """
        logging.info('setting up webdriver')
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)
        #return webdriver.Chrome(options=self.chrome_options)
       

    def load_axe_script(self) -> str:
        """
        Loads the Axe script from the file system.

        Returns:
            str: The content of the Axe script.
        """
        if os.getenv('DOCKER_ENV'):
            # Path for Docker environment
            axe_file_path = os.path.join('/app', 'node_modules', 'axe-core', 'axe.min.js')
        else:
            # Path for local environment
            axe_file_path = os.path.join(os.path.dirname(__file__), '..', 'node_modules', 'axe-core', 'axe.min.js')

        with open(axe_file_path, "r") as axe_file:
            logging.info(f'Opening {axe_file_path}')
            return axe_file.read()
        
    def log_current_url(self, driver: webdriver.Chrome, initial_url: str) -> None:
        """
        Logs the current URL and checks for redirection.

        Args:
            driver (webdriver.Chrome): The Selenium WebDriver instance.
            initial_url (str): The initial URL before any navigation.
        """
        current_url = driver.current_url
        logging.info(f"Initial URL: {initial_url}")
        logging.info(f"Current URL after navigation: {current_url}")
        if initial_url != current_url:
            logging.warning(f"Redirected from {initial_url} to {current_url}. Testing initial URL.")
            driver.execute_script(f"window.location.href='{initial_url}'")

    def inject_axe(self, driver):
        """
        Injects the Axe accessibility testing script into the web page.

        This method reads the `axe.min.js` script from the `node_modules`
        directory and executes it within the context of the currently loaded
        web page, enabling Axe accessibility tests to be performed.

        Args:
            driver (webdriver.Chrome): The Selenium WebDriver instance used to control the browser.

        Returns:
            None
        """
        axe_script = self.load_axe_script() #   
        driver.execute_script(axe_script)
        
    def run_accessibility_tests(self, url: str) -> Optional[Dict]:
        """
        Runs accessibility tests on a single URL.

        Args:
            url (str): The URL to test.

        Returns:
            Optional[Dict]: The results of the accessibility tests, or None if an error occurs.
        """
        #driver = None
        try:
            #driver = self.setup_webdriver()  # Use the setup_webdriver method
            #driver = self.driver
            self.driver.get(url)
            
            # Wait for the page to fully load
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            #WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".back-to-top a .sr-only")))


            self.log_current_url(self.driver, url)

            if self.axe_version == 'Axe 3.1.1':
                axe = Axe(self.driver)
                axe.inject()
                axe_version = self.driver.execute_script("return axe.version;")
                #results = axe.run()
                results = axe.run({
                    "runOnly": {
                    "type": "tag",
                    "values": ["wcag2a", "wcag2aa", "wcag2aaa", "best-practice"]  # All WCAG levels
                    }
                })
            else:
                self.inject_axe(self.driver)
                axe_version = self.driver.execute_script("return axe.version;")
                #results = self.driver.execute_script("return axe.run();")
                # exclude block is for known false positives, should not be used on first testing
                # TODO: solution to exclude certain elements in the ui after first test and confirmation of false positives
                results = self.driver.execute_script("""
                    return axe.run({
                        runOnly: {
                            type: 'tag',
                            values: ['wcag2a', 'wcag2aa', 'wcag2aaa','best-practice']
                        },
                        exclude: [
                            ['.back-to-top a .sr-only'],
                            ['.back-to-top'],
                            ['a[href$="#mainHeader"]'],
                            ['iframe[src*="trustyou.com"]'],
                            ['iframe[src="about:blank"]'],
                            ['.brlbs-cmpnt-cookie-box'],
                            ['.brlbs-cmpnt-preferences-link'],
                            ['.brlbs-cmpnt-privacy-link'],
                            ['.brlbs-cmpnt-imprint-link'],
                            ['#CookieBoxSaveButton'],
                            ['.brlbs-btn-accept-all'],
                            ['.brlbs-btn-accept-only-essential'],
                            ['#CookieBoxPreferencesButton'],
                            ['.brlbs-cmpnt-content-blocker'],
                            ['.brlbs-cmpnt-cb-provider-toggle'],
                            ['[data-borlabs-cookie-content-blocker-id]'],
                            ['[class*="brlbs"]']
                        ]
                    }).then(function(results) {
                        return results;
                    });
                """)


            processor = ResultsProcessor(url, results, self.test_directory)
            processor.save_results_to_json()
            processor.save_results_to_csv()
            return results, axe_version
        except Exception as e:
            logging.error(f"Unexpected error during accessibility testing for {url}: {e}")
            #st.error(f"Unexpected error: {e}")
            logging.debug("Full exception stacktrace", exc_info=True)  # Optional for deeper logs
            return None #####
        
    def test_urls(self, urls: Set[str]) -> Optional[Dict[str, Dict]]:
        """
        Runs accessibility tests on one or multiple URLs.

        Args:
            urls (Set[str]): A set of URLs to test.

        Returns:
            Optional[Dict[str, Dict]]: A dictionary with URLs as keys and test results as values.
        """
        #### Check if URLs are provided
        if not urls:
            logging.warning("No URLs provided for testing.")
            st.warning("No URLs to test.")
            return None, None
        #### Check if URLs are valid

        # use first url to create test directory
        self.test_directory = HelperFunctions.create_test_directory(next(iter(urls)))
    
        results = {}
        axe_version = None
        for url in urls:
            result_and_version = self.run_accessibility_tests(url)
            if not result_and_version:
                logging.warning(f"Test failed or returned no data for {url}")
                st.warning(f"Accessibility test failed or returned no results for: {url}")
                continue

            result, version = result_and_version
            results[url] = result
            if not axe_version:
                axe_version = version
            #result, version = self.run_accessibility_tests(url)
            #if result:
                #results[url] = result
                #if not axe_version: 
                    #axe_version = version
        #self.driver.close()
        #return results if results else None, axe_version
        self.driver.close()

        if not results:
            logging.warning("No accessibility test results were returned.")
            st.error("No accessibility results were generated. Please check your URLs or try again.")
            return None, None

        logging.info(f"Accessibility tests completed for {len(results)} URL(s).")
        return results, axe_version
    def close(self):
        """
        Closes the WebDriver instance.
        """
        if self.driver:
            self.driver.quit()
