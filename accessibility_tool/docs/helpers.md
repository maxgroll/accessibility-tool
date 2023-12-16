# Helpers

The `helpers` module in the Web Accessibility Checker project provides various utility functions used across the application.

## Functions

### `is_url_accessible(url: str) -> bool`

Checks if the given URL is accessible. Returns `True` if accessible, `False` otherwise.

- `url`: The URL to check.

### `create_test_directory(url: str) -> str`

Creates a directory for test results based on the given URL. Returns the path to the created directory.

- `url`: The full URL for which to create the directory structure.

### `is_valid_url(url: str, base_url: str, session: requests.Session) -> bool`

Validates a URL based on specific criteria and content type check. Returns `True` if valid, `False` otherwise.

- `url`: The URL to validate.
- `base_url`: The base URL of the target website.
- `session`: The requests session for making HTTP requests.

### `can_fetch(url: str, user_agent: str = '*') -> bool`

Checks if a URL can be fetched based on the website's robots.txt file. Returns `True` if fetching is allowed, `False` otherwise.

- `url`: The URL to check.
- `user_agent`: The user agent of the crawler (default is '*').

### `get_latest_results_directory(base_results_directory)`

Finds the latest results directory within the given base directory. Returns the path to the latest directory.

- `base_results_directory`: The base directory where test results are stored.

## Example Usage

```python
# Check if a URL is accessible
accessible = is_url_accessible("https://example.com")
print(f"Is the URL accessible? {accessible}")

# Create a test directory
test_dir = create_test_directory("https://example.com")
print(f"Test directory created at: {test_dir}")

# Validate a URL
valid = is_valid_url("https://example.com/page", "https://example.com", session)
print(f"Is the URL valid? {valid}")

# Check if a URL can be fetched according to robots.txt
fetchable = can_fetch("https://example.com/page", user_agent="MyBot")
print(f"Can the URL be fetched? {fetchable}")

# Get the latest results directory
latest_dir = get_latest_results_directory("/path/to/results")
print(f"Latest results directory: {latest_dir}")