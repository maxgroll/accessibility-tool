# util/accessibility_tester.py

import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from axe_selenium_python import Axe
from typing import Dict, Optional, Set
from .results_processor import ResultsProcessor
from util import create_test_directory

class AccessibilityTester:
    """
    A class to run accessibility tests on websites using Axe with Selenium.

    This class handles the initialization of the WebDriver, runs Axe accessibility
    tests on specified URLs, and processes the results.

    Attributes:
        chrome_options (Options): Chrome options for Selenium WebDriver.
    """

    def __init__(self):
        """
        Initializes the AccessibilityTester with Chrome WebDriver options.
        """
        self.test_directory = " "
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")


    def run_accessibility_tests(self, url: str) -> Optional[Dict]:
        """
        Runs accessibility tests on a single URL.

        Args:
            url (str): The URL to test.

        Returns:
            Optional[Dict]: The results of the accessibility tests, or None if an error occurs.
        """

        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(url)
            axe = Axe(driver)
            axe.inject()
            results = axe.run()
            self.test_directory = create_test_directory(url)
            processor = ResultsProcessor(url, results, self.test_directory)
            processor.save_results_to_json()
            processor.save_results_to_csv()
            driver.quit()
            return results
        except Exception as e:
            logging.error(f"Accessibility testing error for {url}: {e}")
            return None

    def test_urls(self, urls: Set[str]) -> Optional[Dict[str, Dict]]:
        """
        Runs accessibility tests on one or multiple URLs.

        Args:
            urls (Set[str]): A set of URLs to test.

        Returns:
            Optional[Dict[str, Dict]]: A dictionary with URLs as keys and test results as values.
        """
        results = {}
        for url in urls:
            result = self.run_accessibility_tests(url)
            if result:
                results[url] = result
        return results if results else None
    
# Example usage:
# tester = AccessibilityTester(url)
# homepage_results = tester.test_homepage("https://example.com")
# selected_urls_results = tester.test_selected_urls(["https://example.com/page1", "https://example.com/page2"])
# all_urls_results = tester.test_all_urls({"https://example.com", "https://example.com/about"})