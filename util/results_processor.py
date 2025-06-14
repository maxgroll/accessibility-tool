# util/results_processor.py

import csv
import json
import logging
import os
from urllib.parse import urlparse


class ResultsProcessor:
    """
    A class to process and save the accessibility test results.

    Attributes:
        url (str): The URL that was tested.
        results (Dict): The results from the Axe accessibility tests.
        test_directory (str): The directory to save the test results.
    """

    def __init__(self, url: str, results: dict, test_directory: str):
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

    def _get_page_identifier(self) -> str:
        """
        Extracts a page-specific identifier from the URL.
        """
        parsed_url = urlparse(self.url)
        domain_name = parsed_url.netloc.replace('www.', '').replace('.', '_')
        page_name = parsed_url.path.strip('/').replace('/', '_') or domain_name
        return page_name

    def save_results_to_json(self) -> None:
        """
        Saves the results in JSON format to the test directory.
        """
        page_identifier = self._get_page_identifier()
        json_filename = os.path.join(self.test_directory, f'{page_identifier}_accessibility_test.json')
        try:
            with open(json_filename, 'w') as json_file:
                json.dump(self.results, json_file, indent=4)
        except OSError as e:
            logging.error(f"Error while saving JSON results for {self.url}: {e}")

    def save_results_to_csv(self) -> None:
        """
        Saves the results in CSV format to the test directory.
        """
        page_identifier = self._get_page_identifier()
        csv_filename = os.path.join(self.test_directory, f'{page_identifier}_accessibility_test.csv')
        try:
            with open(csv_filename, 'w', newline='') as csv_file:
                writer = csv.writer(csv_file)
                
                writer.writerow(['VIOLATIONS', ' ',' ',' ',' ',' ',' ',' ', ' ', ' ', ' '])
                writer.writerow([self.url, ' ',' ',' ',' ',' ',' ',' ', ' ', ' ', ' '])
                writer.writerow(['ID', 'description', 'Impact', 'Help', 'HTML', 'Target', 'Help URL', 'Tags', 'Failure Summary', 'Data', 'Url'])
                for violation in self.results['violations']:
                # Joining tags list into a single string separated by commas
                    tags = ", ".join(violation.get('tags', []))
                    for node in violation['nodes']:
                        # Extract data from the "any" list inside the node
                        data_list: list[str] = []
                        # Function to process the data
                        #def process_data(item):
                        def process_data(item, _d=data_list) -> None:
                            data = item.get('data')
                            if data is None:
                                _d.append(item.get('id'))
                            elif isinstance(data, list):
                                _d.extend(data)
                            elif isinstance(data, dict):
                                _d.append(" | ".join(f"{k}: {v}" for k, v in data.items()))
                            elif isinstance(data, str):
                                _d.append(data)

                        # Check the 'any', 'all', 'none' lists (if present)
                        for key in ("any", "all", "none"):
                            for item in node.get(key, []):
                                process_data(item)

                        # If data_list is still empty, append "No data available"
                        if not data_list:
                            data_list.append("No data available")
            
                        # Join the data elements into a single string
                        flattened_data = " | ".join(data_list)

                        # Ensure all items in 'target' are strings and flatten any nested lists
                        targets = node.get('target', [])
                        flattened_targets = " | ".join([str(target) for sublist in targets for target in (sublist if isinstance(sublist, list) else [sublist])])

                        writer.writerow([
                            violation['id'],
                            violation['description'],
                            violation['impact'],
                            violation['help'],
                            node['html'],
                            flattened_targets,
                            violation['helpUrl'],
                            tags,
                            node['failureSummary'],
                            flattened_data,
                            self.url
                        ])
                # TODO  write another csv for the incomplete tests?
                #writer.writerow(['INCOMPLETE', ' ',' ',' ',' ',' ',' ',' '])
                #writer.writerow([self.url, ' ',' ',' ',' ',' ',' ',' '])
                #writer.writerow(['ID', 'description', 'Impact', 'Help', 'HTML', 'Target', 'Help URL', 'Tags'])
               # for violation in self.results['incomplete']:
                # Joining tags list into a single string separated by commas
                    #tags = ", ".join(violation.get('tags', []))
                    #for node in violation['nodes']:
                       
                        #writer.writerow([
                            #violation['id'],
                            #violation['description'],
                            #violation['impact'],
                            #violation['help'],
                            #node['html'],
                            #" | ".join(node['target']),
                            #violation['helpUrl'],
                            #tags
                        #])
        except OSError as e:
            logging.error(f"Error while saving CSV results for {self.url}: {e}")
 

# Example usage
if __name__ == "__main__":
    # Assume some results are obtained from accessibility testing
    url = "https://example.com"
    from typing import Any
    results: dict[str, Any] = {}  # Placeholder for actual Axe results
    test_directory: str = "/path/to/directory"
    processor = ResultsProcessor(url, results, test_directory)
    processor.save_results_to_json()
    processor.save_results_to_csv()