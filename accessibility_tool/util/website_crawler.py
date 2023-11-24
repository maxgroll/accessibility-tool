# website_crawler.py

from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from typing import Set
import logging

from util import is_valid_url


class WebsiteCrawler:
    """
    A class to crawl a website and gather all accessible URLs.

    This crawler respects the 'nofollow' directive in hyperlinks and supports setting a maximum crawl depth.

    Attributes:
        root_url (str): The base URL of the website to crawl.
        crawled_urls (Set[str]): A set of URLs found during crawling.
        hostname (str): The hostname of the root URL.
    """

    def __init__(self, root_url: str):
        self.root_url: str = root_url
        self.crawled_urls: Set[str] = set()
        self.hostname: str = urlparse(root_url).hostname
    
    def crawl(self, url: str, max_depth: int = 3, current_depth: int = 0) -> None:
        """
        Recursively crawl a website starting from a root URL up to a maximum depth.

        Args:
            url (str): The starting URL to crawl from.
            max_depth (int): The maximum depth to crawl.
            current_depth (int): The current depth of the crawl.

        Returns:
            None
        """
        
        if current_depth > max_depth:
            return
        
        parsed_url = urlparse(url)
        
        # Ignore URLs that do not start with http or https
        if parsed_url.scheme not in ['http', 'https']:
            logging.info(f"Ignored non-http(s) URL: {url}")
            return
        # Ignore URLs that do not start with the root URLs
        if not url.startswith(self.root_url):
            logging.info(f"Ignored external URL: {url}")
            return
        # Ignore Urls with parameteres
        if parsed_url.fragment or parsed_url.query:
            logging.info(f"Ignored internal URL: {url}")
            return

        try:
            response = requests.get(url)
            if response.status_code == 200:
                clean_url = urlparse(url)._replace(fragment='').geturl()
                if clean_url not in self.crawled_urls and is_valid_url(clean_url, self.root_url):
                #if clean_url not in self.crawled_urls:
                    self.crawled_urls.add(clean_url)
                    logging.info(f"Added: {clean_url}")
                    soup = BeautifulSoup(response.content, "html.parser")
                    for link in soup.find_all('a', href=True):
                        if link.get('rel') == ['nofollow']:
                            continue # Skip 'nofollow' links
                        href = link.get('href')
                        parsed_href = urlparse(href)
                        new_url = href if parsed_href.hostname == self.hostname else urljoin(self.root_url, href)

                        if new_url not in self.crawled_urls:
                            self.crawl(new_url, max_depth, current_depth + 1)
        except requests.RequestException as e:
            logging.info(f"Error crawling URL {url}: {e}")

    def get_crawled_urls(self) -> Set[str]:
        """
        Get the set of crawled URLs.

        Returns:
            Set[str]: A set of crawled URLs.
        """
        return self.crawled_urls

    def crawl_urls_to_test(self, url: str, crawl_depth: int) -> Set[str]:
        """
        Initiates crawling from the given URL up to the specified depth.

        Args:
            url (str): The URL to start crawling from.
            crawl_depth (int): The depth of crawling.

        Returns:
            Set[str]: A set of URLs crawled up to the specified depth.
        """

        self.crawl(url, max_depth=crawl_depth)
        logging.info(f"Crawling {url} finished")
        return self.get_crawled_urls()


# Example usage
#if __name__ == "__main__":
    #crawler = WebsiteCrawler("https://digitalagenten.com")
    #crawler.crawl("https://digitalagenten.com")
    #crawled_urls = crawler.get_crawled_urls()
    #print(len(crawled_urls))