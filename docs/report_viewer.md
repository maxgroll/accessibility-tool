# Accessibility Report Viewer

The `AccessibilityReportViewer` class is designed to visualize and interpret the results of accessibility tests.

## Class Attributes

- `results_path` (str): Path to the JSON file containing the test results.

## Methods

### `__init__(self, results_path: str)`

Constructor for the class.

- `results_path`: Path to the JSON file containing the test results.

### `calculate_accessibility_score(self) -> float`

Calculates the overall accessibility score based on the test results.

### `extract_critical_violations(self) -> List[Dict]`

Extracts and returns a list of critical violations from the test results.

### `create_violations_dataframe(self) -> pd.DataFrame`

Creates a pandas DataFrame with detailed information about all violations.

## Example Usage

```python
report_viewer = AccessibilityReportViewer("/path/to/results.json")
score = report_viewer.calculate_accessibility_score()
print(f"Accessibility Score: {score}%")

critical_violations = report_viewer.extract_critical_violations()
for violation in critical_violations:
    print(violation)

violations_df = report_viewer.create_violations_dataframe()
print(violations_df)