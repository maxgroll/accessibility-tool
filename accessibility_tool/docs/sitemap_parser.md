# Sitemap Parser

The `SitemapParser` class is designed to parse sitemaps and sitemap indexes from websites, handling different sitemap formats, including sitemaps with query parameters.

## Class Attributes

- `base_url` (str): The base URL of the website to check for a sitemap.
- `sitemap_urls` (Set[str]): A set containing URLs found in the sitemap.

## Methods

### `__init__(self, base_url: str)`

Constructor for the class.

- `base_url`: The base URL of the website whose sitemap is to be parsed.

### `fetch_sitemap(self, sitemap_url: str) -> Optional[bytes]`

Fetches the sitemap from a given URL.

- `sitemap_url`: URL of the sitemap to fetch.

### `fetch_sitemap_from_robots(self) -> Optional[str]`

Fetches the sitemap URL from the robots.txt file.

### `parse_sitemap_index(self, content: bytes)`

Parses the sitemap index to find individual sitemap files.

- `content`: Content of the sitemap index.

### `parse_sitemap(self, content: bytes)`

Parses the sitemap content and adds found URLs to the set.

- `content`: Content of the sitemap.

### `has_sitemap(self) -> bool`

Checks if the website has a sitemap or sitemap index and returns a boolean.

### `get_sitemap_urls(self) -> Set[str]`

Returns the set of URLs found in the sitemap.

## Example Usage

```python
sitemap_parser = SitemapParser("https://example.com")
if sitemap_parser.has_sitemap():
    urls = sitemap_parser.get_sitemap_urls()
    print(f"URLs found in the sitemap: {len(urls)}")