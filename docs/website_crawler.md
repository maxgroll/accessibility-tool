# Website Crawler

The `WebsiteCrawler` class is responsible for crawling a website and collecting all accessible URLs.

## Class Attributes

- `root_url` (str): The base URL of the website to crawl.
- `crawled_urls` (Set[str]): A set of URLs that have been found during crawling.
- `hostname` (str): The hostname extracted from the `root_url`.

## Methods

### `__init__(self, root_url: str, user_agent: str = '*')`

Constructor for the class.

- `root_url`: The base URL for the website to crawl.
- `user_agent`: The user agent to use for crawling. Defaults to '*'.

### `crawl(self, url: str, max_depth: int = 3, current_depth: int = 0)`

Recursively crawls a website starting from a root URL up to a maximum depth.

- `url`: The starting URL to crawl from.
- `max_depth`: The maximum depth to crawl.
- `current_depth`: The current depth of the crawl.

### `get_crawled_urls(self)`

Returns the set of crawled URLs.

### `crawl_urls_to_test(self, url: str, crawl_depth: int)`

Initiates crawling from the given URL up to the specified depth.

- `url`: The URL to start crawling from.
- `crawl_depth`: The depth of crawling.

## Example Usage

```python
crawler = WebsiteCrawler("https://example.com/")
crawler.crawl_urls_to_test("https://example.com/", 3)
crawled_urls = crawler.get_crawled_urls()
print(f"Number of URLs found: {len(crawled_urls)}")