import json
import csv
import os
import logging
from typing import Dict

def process_accessibility_results(url: str, results: Dict, test_directory: str) -> None:
    """
    Processes and saves the accessibility test results to JSON and CSV files in the specified directory.

    Args:
        url (str): The URL that was tested.
        results (Dict): The results from the Axe accessibility tests.
        test_directory (str): The directory to save the test results.

    Raises:
        IOError: An error occurred when writing the results to files.
    """
    try:
        # Save results in JSON format
        json_filename = os.path.join(test_directory, 'accessibility_test.json')
        with open(json_filename, 'w') as json_file:
            json.dump(results, json_file, indent=4)

        # Save results in CSV format
        csv_filename = os.path.join(test_directory, 'accessibility_test.csv')
        with open(csv_filename, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['URL', 'ID', 'Impact', 'Help', 'HTML', 'Target', 'Help URL'])
            for violation in results['violations']:
                for node in violation['nodes']:
                    writer.writerow([
                        url,
                        violation['id'],
                        violation['impact'],
                        violation['help'],
                        node['html'],
                        " | ".join(node['target']),
                        violation['helpUrl']
                    ])
    except IOError as e:
        logging.error(f"Error while saving accessibility test results for {url}: {e}")
