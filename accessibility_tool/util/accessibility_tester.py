# accessibility_tester.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from axe_selenium_python import Axe
from .results_processor import process_accessibility_results


def run_accessibility_tests(url):
    """
    Runs accessibility tests on a given URL using Axe with Selenium.

    Args:
        url (str): The URL to test for accessibility issues.

    Returns:
        dict: The results of the accessibility tests.
    """
    try:
        # Set up Chrome options for Selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Ensure GUI is off
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
        chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

        # Initialize WebDriver
        driver = webdriver.Chrome(options=chrome_options)

        # Navigate to the page
        driver.get(url)

        # Initialize Axe for accessibility testing
        axe = Axe(driver)
        axe.inject()
        results = axe.run()

        # Process results (e.g., save to a file or return them)
        process_accessibility_results(url, results)

        # Quit the driver
        driver.quit()

        return results

    except Exception as e:
        print(f"Error occurred while running accessibility tests for {url}: {e}")
        return {}

# This allows the module to be used both as a script and as an importable module
if __name__ == "__main__":
    # Example usage:
    url = "https://example.com"
    results = run_accessibility_tests(url)
    print(results)
