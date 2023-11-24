# sitemap_parser.py
# TODO fix class so it can parse diverse types of sitemaps
# https://www.hhi.fraunhofer.de/sitemap.xml does NOT get parsed
# https://digitalagenten.com/sitemap_index.xml does get parsed
import requests
import logging
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
from typing import Optional, Set

class SitemapParser:
    """
    A class to parse sitemaps and sitemap indexes from websites.

    This class handles different formats of sitemaps including those with query parameters.
    It can parse both individual sitemaps and sitemap indexes.

    Attributes:
        base_url (str): The base URL of the website for which the sitemap is to be parsed.
        sitemap_urls (Set[str]): A set of URLs found in the sitemap.
        namespace (dict): The namespace mapping for XML parsing.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.sitemap_urls = set()
        self.namespace = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    def fetch_sitemap(self, sitemap_url: str) -> Optional[bytes]:
        """
        Fetches the sitemap from a given URL.

        Args:
            sitemap_url (str): The URL of the sitemap.

        Returns:
            Optional[bytes]: The content of the sitemap if successful, None otherwise.
        """

        try:
            # Handle cases where sitemap URL includes query parameters
            parsed_url = urlparse(sitemap_url)
            if parsed_url.query:
                # If there are query parameters, make sure to send a GET request with those params
                base_url = urljoin(sitemap_url, urlparse(sitemap_url).path)
                params = dict(param.split('=') for param in parsed_url.query.split('&'))
                response = requests.get(base_url, params=params)
            else:
                response = requests.get(sitemap_url)

            if response.status_code == 200:
                return response.content
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred while fetching the sitemap: {e}")
        except ValueError as e:
            # This might happen if the sitemap URL's query parameters are malformed
            logging.error(f"An error occurred while parsing the sitemap URL: {e}")
        return None
    
    def fetch_sitemap_from_robots(self) -> Optional[str]:
        """
        Checks the robots.txt file for the sitemap URL.
        """
        # TODO Implement finding and parsing robots.txt for sitemap(s)
        # Check https://docs.python.org/3/library/urllib.robotparser.html
        # Check https://www.python-httpx.org/api/
        # Check https://softhints.com/read-parse-test-robots-txt-python/
        # Check https://practicaldatascience.co.uk/data-science/how-to-parse-xml-sitemaps-using-python
        
        pass

    def parse_sitemap_index(self, content: bytes) -> None:
        """
        Parses the sitemap index content to find individual sitemap files.
        Then fetches and parses each individual sitemap file.

        Args:
            content (bytes): The XML content of the sitemap index file.
        """
        try:
            root = ET.fromstring(content)
            sitemap_tags = root.findall('sitemap:sitemap', self.namespace)
            for sitemap in sitemap_tags:
                loc = sitemap.find('sitemap:loc', self.namespace)
                if loc is not None:
                    sitemap_url = loc.text
                    logging.info(f"Found sitemap in index: {sitemap_url}")
                    sitemap_content = self.fetch_sitemap(sitemap_url)
                    if sitemap_content:
                        self.parse_sitemap(sitemap_content)
                    else:
                        logging.error(f"Could not fetch content from sitemap: {sitemap_url}")
        except ET.ParseError as e:
            logging.error(f"An error occurred while parsing the sitemap index content: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")


    def parse_sitemap(self, content: bytes) -> None:
        """
        Parses the sitemap content and adds found URLs to the set.

        Args:
            content (bytes): The XML content of the sitemap.
        """

        try:
            root = ET.fromstring(content)
            # Log the content to see what is being parsed
            #logging.info(f"Sitemap content: {content}")
            url_tags = root.findall('sitemap:url', self.namespace)
            for url_tag in url_tags:
                loc = url_tag.find('sitemap:loc', self.namespace)
                if loc is not None:
                    self.sitemap_urls.add(loc.text)
        except ET.ParseError as e:
            logging.info(f"An error occurred while parsing the sitemap content: {e}")

    def has_sitemap(self) -> bool:
        """
        Checks if the website has a sitemap or sitemap index.

        Returns:
            bool: True if a sitemap or sitemap index exists, False otherwise.
        """

        # TODO implement logic get sitemap(s) from self.fetch_sitemap_from_robots()
        
        sitemap_index_url = urljoin(self.base_url, 'sitemap_index.xml')
        content = self.fetch_sitemap(sitemap_index_url)
        if content and '<sitemapindex' in content.decode('utf-8'):
            self.parse_sitemap_index(content)
            return True

        sitemap_url = urljoin(self.base_url, 'sitemap.xml')
        content = self.fetch_sitemap(sitemap_url)
        if content:
            self.parse_sitemap(content)
            return True

        return False

    def get_sitemap_urls(self) -> Set[str]:
        """
        Returns the set of URLs found in the sitemap.

        Returns:
            Set[str]: A set of URLs from the sitemap.
        """

        return self.sitemap_urls
