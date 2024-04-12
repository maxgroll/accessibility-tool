# Results Processor

The `ResultsProcessor` class is responsible for processing the results of accessibility tests and generating reports.

## Class Attributes

- `url` (str): The URL of the webpage that was tested.
- `results` (Dict): The results of the accessibility tests.
- `test_directory` (str): The directory where the test results are stored.

## Methods

### `__init__(self, url: str, results: Dict, test_directory: str)`

Constructor for the class.

- `url`: The URL of the webpage that was tested.
- `results`: The results of the accessibility tests.
- `test_directory`: The directory where the test results are stored.

### `save_results_to_json(self)`

Saves the test results to a JSON file in the specified directory.

### `save_results_to_csv(self)`

Saves the test results to a CSV file in the specified directory.

### `extract_critical_violations(self) -> List[Dict]`

Extracts and returns a list of critical violations from the test results.

## Example Usage

```python
processor = ResultsProcessor("https://example.com", test_results, "/path/to/test_directory")
processor.save_results_to_json()
processor.save_results_to_csv()
critical_violations = processor.extract_critical_violations()
for violation in critical_violations:
    print(violation)