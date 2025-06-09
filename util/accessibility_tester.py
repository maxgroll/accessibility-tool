# util/accessibility_tester.py
import logging
import os

import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from typing import Any, Optional, Tuple, Set, Dict

from util.helper_functions import HelperFunctions
from util.results_processor import ResultsProcessor


class AccessibilityTester:
    """
    Crawl-agnostic axe-core runner.
    Always fetches the latest axe.min.js from the CDN at runtime.
    """

    def __init__(self) -> None:
        self.test_directory: str = ""

        #opts = Options()
        #opts.add_argument("--headless")
        #opts.add_argument("--disable-gpu")
        #opts.add_argument("--no-sandbox")
        #opts.add_argument("--disable-dev-shm-usage")
        #opts.add_argument("--window-size=1920x1080")

        #self.driver = webdriver.Chrome(
            #service=Service(ChromeDriverManager().install()),
            #options=opts,
        #)
        self.driver = self._setup_webdriver()
        # download latest axe script once per tester instance
        self._axe_script = HelperFunctions.fetch_latest_axe()

    # ──────────────────────────────────────────────────────────────
    # choose driver depending on env
    # ──────────────────────────────────────────────────────────────
    def _setup_webdriver(self) -> webdriver.Chrome:
        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--window-size=1920x1080")

        if os.getenv("DOCKER_ENV", "").lower() == "true":
            logging.info("Docker environment detected – using system chromedriver")
            return webdriver.Chrome(service=Service("/usr/bin/chromedriver"),
                                    options=opts)
        else:
            logging.info("Local environment – using webdriver_manager")
            return webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                                    options=opts)

    # ------------------------------------------------------------------ #
    # Core helpers                                                        #
    # ------------------------------------------------------------------ #
    def _inject_axe(self) -> None:
        """Inject the downloaded axe.min.js into the current page."""
        self.driver.execute_script(self._axe_script)

    #def _run_for_url(self, url: str) -> dict | None:
    def _run_for_url(self, url: str) -> Optional[Tuple[Dict[str, Any], str]]:
        """
        Navigate to `url`, inject axe, run audit, save JSON/CSV.
        Returns (results_json, axe_version) or None on failure.
        """
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            self._inject_axe()
            axe_version = self.driver.execute_script("return axe.version;")

            results = self.driver.execute_script(
                """
                return axe.run({
                    runOnly: { type: 'tag',
                               values: ['wcag2a','wcag2aa','wcag2aaa','best-practice'] },
                }).then(r => r);
                """
            )

            proc = ResultsProcessor(url, results, self.test_directory)
            proc.save_results_to_json()
            proc.save_results_to_csv()

            return results, axe_version

        except Exception as exc:
            logging.error("axe test failed for %s: %s", url, exc, exc_info=True)
            return None

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #
    #def test_urls(self, urls: set[str]):
    def test_urls(self, urls: Set[str]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Run axe on each URL in `urls`.
        Returns (result_dict, axe_version) or (None, None) if nothing succeeded.
        """
        if not urls:
            st.warning("No URLs to test.")
            return None, None

        # create timestamped results directory based on first URL
        from util.helper_functions import HelperFunctions  # avoid circular import
        self.test_directory = HelperFunctions.create_test_directory(next(iter(urls)))

        all_results, axe_ver = {}, None
        for url in urls:
            outcome = self._run_for_url(url)
            if not outcome:
                st.warning(f"No results for {url}")
                continue
            res, ver = outcome
            all_results[url] = res
            axe_ver = axe_ver or ver

        self.driver.quit()

        if not all_results:
            st.error("No accessibility results generated.")
            return None, None

        return all_results, axe_ver

    # optional explicit close
    def close(self):
        if self.driver:
            self.driver.quit()

