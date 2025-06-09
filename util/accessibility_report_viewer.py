import json

import pandas as pd


class AccessibilityReportViewer:
    def __init__(self, json_file):
        # Load the JSON data from the file upon initialization
        with open(json_file) as file:
            self.data = json.load(file)
    

    def calculate_accessibility_score(self):
        # Impact weights for different levels of severity
        impact_weights = {
            'critical': 3,#3
            'serious': 2,#2
            'moderate': 1,#1
            'minor': 0.75 #0.75
        }

        # Base score starts at 100
        base_score = 100
        total_penalty = 0

        # Calculate the penalty for each violation based on its impact level
        for violation in self.data['violations']:
            impact_level = violation['impact']
            weight = impact_weights.get(impact_level, 0)  # Default to 0 if impact level not found
            total_penalty += weight

        # Calculate the number of checks
        total_checks = (len(self.data['violations']) + 
                        len(self.data['passes']) + 
                        len(self.data['incomplete']) + 
                        len(self.data['inapplicable']))
        
        # Avoid division by zero
        if total_checks == 0:
            return 100  # No issues found, return the best score
        
        # Calculate the final accessibility score considering the total penalty and checks
        adjusted_score = base_score - (total_penalty / total_checks * base_score)

        # Ensure the score does not go below 0
        adjusted_score = max(adjusted_score, 0)

        return adjusted_score




    def extract_critical_violations(self):
        # List to hold critical violations
        critical_violations = []

        # Extract critical violations
        for item in self.data['violations']:
            if item['impact'] == 'critical':
                critical_violations.append({
                    'description': item['description'],
                    'help': item['help'],
                    'helpUrl': item['helpUrl'],
                    'nodes': item['nodes'],  # This contains detailed information about each violation
                })

        return critical_violations
    

    def create_violations_dataframe(self):
    #with open(result_path, 'r') as json_file:
        #results = json.load(json_file)
    
    # Extract the data needed for the dataframe
        data_rows = []
        for violation in self.data['violations']:
            for node in violation['nodes']:
                # Extract data from the "any" list inside the node
                any_list = node.get('any', [])
                #data_list = [item.get('data', []) for item in any_list if item.get('data') is not None]
                data_list = []
                for item in any_list:
                    data = item.get('data', [])
                    if isinstance(data, list):
                        data_list.extend(data)
                    else:
                        data_list.extend([data])
                # Flatten and join the data elements
                #flattened_data = " | ".join([data_item for sublist in data_list for data_item in sublist])
                flattened_data = " | ".join([str(data_item) for data_item in data_list])

                targets = node.get('target', [])
                flattened_targets = " | ".join([str(target) for sublist in targets for target in (sublist if isinstance(sublist, list) else [sublist])])


                data_rows.append({
                    #'URL': violation.get('url', ''),
                    'ID': violation.get('id', ''),
                    'Description': violation.get('description', ''),
                    'Impact': violation.get('impact', ''),
                    'Help': violation.get('help', ''),
                    'HTML': node.get('html', ''),
                    'Target': flattened_targets,
                    #'Target': " | ".join(node.get('target', [])),
                    'Help URL': violation.get('helpUrl', ''),
                    'Tags': violation.get('tags', ''),
                    'FailureSummary': node.get('failureSummary', ''),
                    'Data': flattened_data,
                    'Url' : self.data['url']
                })
    
        # Create the dataframe
        df = pd.DataFrame(data_rows)
        return df

# Example usage
#json_file = 'path_to_your_json_file'  # Replace with your actual JSON file path
#report_viewer = AccessibilityReportViewer(json_file)
#accessibility_score = report_viewer.calculate_accessibility_score()
#print(f"Accessibility Score: {accessibility_score}%")

#critical_violations = report_viewer.extract_critical_violations()
#for violation in critical_violations:
    #print(violation)
