# results_processor.py

import json
import csv
import os
import logging
from typing import Dict

class ResultsProcessor:
    """
    A class to process and save the accessibility test results.

    Attributes:
        url (str): The URL that was tested.
        results (Dict): The results from the Axe accessibility tests.
        test_directory (str): The directory to save the test results.
    """

    def __init__(self, url: str, results: Dict, test_directory: str):
        """
        Initializes the ResultsProcessor with URL, results, and test directory.

        Args:
            url (str): The URL that was tested.
            results (Dict): The results from the Axe accessibility tests.
            test_directory (str): The directory to save the test results.
        """
        self.url = url
        self.results = results
        self.test_directory = test_directory

    def save_results_to_json(self) -> None:
        """
        Saves the results in JSON format to the test directory.
        """
        json_filename = os.path.join(self.test_directory, 'accessibility_test.json')
        try:
            with open(json_filename, 'w') as json_file:
                json.dump(self.results, json_file, indent=4)
        except IOError as e:
            logging.error(f"Error while saving JSON results for {self.url}: {e}")

    def save_results_to_csv(self) -> None:
        """
        Saves the results in CSV format to the test directory.
        """
        csv_filename = os.path.join(self.test_directory, 'accessibility_test.csv')
        try:
            with open(csv_filename, 'w', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(['URL', 'ID', 'Impact', 'Help', 'HTML', 'Target', 'Help URL'])
                for violation in self.results['violations']:
                    for node in violation['nodes']:
                        writer.writerow([
                            self.url,
                            violation['id'],
                            violation['impact'],
                            violation['help'],
                            node['html'],
                            " | ".join(node['target']),
                            violation['helpUrl']
                        ])
        except IOError as e:
            logging.error(f"Error while saving CSV results for {self.url}: {e}")

    

# Example usage
if __name__ == "__main__":
    # Assume some results are obtained from accessibility testing
    url = "https://example.com"
    results = {}  # Placeholder for actual results
    test_directory = "/path/to/directory"
    processor = ResultsProcessor(url, results, test_directory)
    processor.save_results_to_json()
    processor.save_results_to_csv()