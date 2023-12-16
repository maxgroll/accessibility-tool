# test_website_crawler.py

import pytest
from urllib.parse import urlparse
from ..accessibility_tool.util.website_crawler import WebsiteCrawler

class TestWebsiteCrawler:
    @pytest.fixture
    def crawler(self):
        # Initialize WebsiteCrawler with a known website
        return WebsiteCrawler("https://digitalagenten.com/")

    def test_crawl(self, crawler):
        # Only crawl to a depth of 1 to keep the test quick and simple
        crawler.crawl_urls_to_test(crawler.root_url, 1)
        crawled_urls = crawler.get_crawled_urls()
        
        # Check if the root_url is in the crawled URLs
        assert crawler.root_url in crawled_urls
        
        # Check that some URLs have been found
        assert len(crawled_urls) > 0

    def test_crawl_with_invalid_url(self, crawler):
        # Attempt to crawl an invalid URL
        invalid_url = "https://thisdoesnotexist.example.com/"
        crawler.crawl_urls_to_test(invalid_url, 1)
        crawled_urls = crawler.get_crawled_urls()
        
        # Check that no URLs have been found
        assert len(crawled_urls) == 0

    def test_crawl_with_depth(self, crawler):
        # Test crawling with a specific depth
        depth = 2
        crawler.crawl_urls_to_test(crawler.root_url, depth)
        crawled_urls = crawler.get_crawled_urls()
        
        # Check that the URLs crawled are not just from the first level
        # This is a simplified check and might need to be adjusted based on the website structure
        assert any(urlparse(url).path.count('/') >= depth for url in crawled_urls)