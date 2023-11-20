# website_crawler.py

from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from typing import Set
import logging

from util import is_valid_url

class WebsiteCrawler:
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

        try:
            response = requests.get(url)
            if response.status_code == 200:
                clean_url = urlparse(url)._replace(fragment='').geturl()
                if clean_url not in self.crawled_urls and is_valid_url(clean_url, self.root_url):
                    self.crawled_urls.add(clean_url)
                    soup = BeautifulSoup(response.content, "html.parser")
                    for link in soup.find_all('a', href=True):
                        href = link.get('href')
                        if link.get('rel') == ['nofollow']:
                            continue
                        parsed_href = urlparse(href)
                        new_url = href if parsed_href.hostname == self.hostname else urljoin(self.root_url, href)

                        if new_url not in self.crawled_urls:
                            self.crawl(new_url, max_depth, current_depth + 1)
        except requests.RequestException as e:
            logging.info(f"Error retrieving URL {url}: {e}")

    def get_crawled_urls(self) -> Set[str]:
        """
        Get the set of crawled URLs.

        Returns:
            Set[str]: A set of crawled URLs.
        """
        return self.crawled_urls


# Example usage
#if __name__ == "__main__":
    #crawler = WebsiteCrawler("https://digitalagenten.com")
    #crawler.crawl("https://digitalagenten.com")
    #crawled_urls = crawler.get_crawled_urls()
    #print(len(crawled_urls))