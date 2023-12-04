# website_crawler.py

from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from typing import Set
import logging

from util.helpers import is_valid_url, can_fetch
#from helpers import is_valid_url, can_fetch

#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
class WebsiteCrawler:
    """
    A class to crawl a website and gather all accessible URLs.

    This crawler respects the 'nofollow' directive in hyperlinks and supports setting a maximum crawl depth.

    Attributes:
        root_url (str): The base URL of the website to crawl.
        crawled_urls (Set[str]): A set of URLs found during crawling.
        hostname (str): The hostname of the root URL.
    """

    def __init__(self, root_url: str, user_agent: str = '*'):
        self.root_url = root_url
        self.crawled_urls: Set[str] = set()
        self.hostname = urlparse(root_url).hostname
        self.user_agent = user_agent
        self.session = requests.Session()  # Session for repeated requests
    
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
        #logging.info(f"Crawling URL: {url} at depth {current_depth}")
        if current_depth > max_depth:
            return
        
        if is_valid_url(url, self.root_url, self.session) and can_fetch(url, self.user_agent):
        #if is_valid_url(url, self.root_url, self.session):
       
            try:
                response = self.session.get(url)
                #logging.info(f"HTTP response for {url}: {response.status_code}")
                if response.status_code == 200:
                    clean_url = urlparse(url)._replace(fragment='').geturl()
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
        #logging.info(f"Starting crawl for {url} with depth {crawl_depth}")
        self.crawl(url, max_depth=crawl_depth)
        logging.info(f"Crawling {url} finished with {len(self.crawled_urls)} URLs found")
        return self.get_crawled_urls()


# Example usage
#if __name__ == "__main__":
    #crawler = WebsiteCrawler("https://maxgroll.github.io/LaZona/")
    #crawler.crawl_urls_to_test("https://maxgroll.github.io/LaZona/", 3)
    #crawled_urls = crawler.get_crawled_urls()
    #print(len(crawled_urls))