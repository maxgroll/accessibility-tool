import json
import csv
import os


def process_accessibility_results(url, results, test_directory):
    """
    Processes and saves the accessibility test results to JSON and CSV files.

    Args:
        url (str): The URL that was tested.
        results (dict): The results from the Axe accessibility tests.
    """
    #json_filename = os.path.join(results_dir, 'accessibility_test.json')
    json_filename = os.path.join(test_directory, 'accessibility_test.json')
    with open(json_filename, 'w') as json_file:
        json.dump(results, json_file, indent=4)

    # Save results in CSV format
    #csv_filename = os.path.join(results_dir, 'accessibility_test.csv')
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

