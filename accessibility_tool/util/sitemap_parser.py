# util/sitemap_parser.py

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
    """

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.sitemap_urls: Set[str] = set()
        self.namespace = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    def fetch_sitemap(self, sitemap_url: str) -> Optional[bytes]:
        """
        Fetches the sitemap from a given URL.
        """
        try:
            parsed_url = urlparse(sitemap_url)
            if parsed_url.query:
                base_url = urljoin(sitemap_url, parsed_url.path)
                params = dict(param.split('=') for param in parsed_url.query.split('&'))
                response = requests.get(base_url, params=params)
            else:
                response = requests.get(sitemap_url)

            if response.status_code == 200:
                return response.content
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred while fetching the sitemap: {e}")
        except ValueError as e:
            logging.error(f"An error occurred while parsing the sitemap URL: {e}")
        return None

    def fetch_sitemap_from_robots(self) -> Optional[str]:
        """
        Fetches sitemap URL from the robots.txt file of the base_url domain.
        """
        robots_url = urljoin(self.base_url, 'robots.txt')
        try:
            response = requests.get(robots_url)
            if response.status_code == 200:
                for line in response.text.split('\n'):
                    if line.startswith('Sitemap: '):
                        sitemap_url = line.split('Sitemap: ')[1].strip()
                        return sitemap_url
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred while fetching robots.txt: {e}")
        return None

    def parse_sitemap_index(self, content: bytes) -> None:
        """
        Parses the sitemap index content to find individual sitemap files.
        """
        try:
            root = ET.fromstring(content)
            if root.tag != '{http://www.sitemaps.org/schemas/sitemap/0.9}sitemapindex':
                logging.error("Not a valid sitemap index file.")
                return  # This is not a sitemap index file
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
        """
        try:
            root = ET.fromstring(content)
            if root.tag != '{http://www.sitemaps.org/schemas/sitemap/0.9}urlset':
                logging.error("Not a valid sitemap file.")
                return  # This is not a sitemap index file
            ignored_segments = [
                'elementor-hf', 'wp-content', 'wp-includes', 'wp-admin', 'feed', 'elementor', 
                'components', 'templates', 'plugins', 'node', 'user', 'catalog',  'author'
                'checkout', 'customer', 'collections', 'products', 'app', 'site'
            ]
            url_tags = root.findall('sitemap:url', self.namespace)
            for url_tag in url_tags:
                loc = url_tag.find('sitemap:loc', self.namespace)
                if loc is not None:
                    url = loc.text
                    if not any(segment in url.lower().split('/') for segment in ignored_segments):
                        self.sitemap_urls.add(loc.text)
        except ET.ParseError as e:
            logging.error(f"An error occurred while parsing the sitemap content: {e}")

    def has_sitemap(self) -> bool:
        """
        Checks if the website has a sitemap or sitemap index.
        Returns False if a parse error occurs or no URLs are found.

        Returns:
            bool: True if a sitemap or sitemap index exists and is well-formed, False otherwise.
        """

        # Attempt to fetch sitemap from robots.txt first
        sitemap_url_from_robots = self.fetch_sitemap_from_robots()
        if sitemap_url_from_robots:
            content = self.fetch_sitemap(sitemap_url_from_robots)
            if content:
                try:
                    if '<sitemapindex' in content.decode('utf-8'):
                        self.parse_sitemap_index(content)
                    else:
                        self.parse_sitemap(content)
                    return True if self.sitemap_urls else False
                except ET.ParseError:
                    logging.error(f"Parse error encountered for sitemap found in robots.txt: {sitemap_url_from_robots}")
                    return False

        # Fallback to checking for sitemap_index.xml and sitemap.xml
        for sitemap_path in ['sitemap_index.xml', 'sitemap.xml']:
            sitemap_url = urljoin(self.base_url, sitemap_path)
            content = self.fetch_sitemap(sitemap_url)
            if content:
                try:
                    if '<sitemapindex' in content.decode('utf-8'):
                        self.parse_sitemap_index(content)
                    else:
                        self.parse_sitemap(content)
                    if self.sitemap_urls:  # If any URLs were added
                        return True
                except ET.ParseError:
                    logging.error(f"Parse error encountered for {sitemap_path}")
                    continue  # Continue trying the next sitemap option

        return False  # No sitemaps found or parse error encountered

    def get_sitemap_urls(self) -> Set[str]:
        """
        Returns the set of URLs found in the sitemap.
        """
        return self.sitemap_urls