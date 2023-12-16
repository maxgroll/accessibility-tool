# Accessibility Tester

The `AccessibilityTester` class is responsible for running accessibility tests on websites using Axe with Selenium.

## Class Attributes

- `chrome_options` (Options): Chrome options for Selenium WebDriver.

## Methods

### `__init__(self)`

Constructor for the class. Initializes the `AccessibilityTester` with Chrome WebDriver options.

### `run_accessibility_tests(self, url: str) -> Optional[Dict]`

Runs accessibility tests on a single URL.

- `url` (str): The URL to test.

Returns a dictionary containing the results of the accessibility tests, or None if an error occurs.

### `test_urls(self, urls: Set[str]) -> Optional[Dict[str, Dict]]`

Runs accessibility tests on one or multiple URLs.

- `urls` (Set[str]): A set of URLs to test.

Returns a dictionary with URLs as keys and test results as values.

## Example Usage

```python
tester = AccessibilityTester()
results = tester.test_urls({"https://example.com", "https://example.com/about"})
for url, result in results.items():
    print(f"Accessibility test results for {url}: {result}")