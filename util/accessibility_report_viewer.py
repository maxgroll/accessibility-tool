import json
import pandas as pd

class AccessibilityReportViewer:
    def __init__(self, json_file):
        # Load the JSON data from the file upon initialization
        with open(json_file) as file:
            self.data = json.load(file)
    

    def calculate_accessibility_score(self):
        # Initialize counters for different impact levels
        p2 = p1 = p0 = 0

        # Iterate over violations and count them by impact level
        for item in self.data['violations']:
            
            if item['impact'] in ['critical', 'serious']:
                p2 += 1
            elif item['impact'] == 'moderate':
                p1 += 1
            elif item['impact'] == 'minor':
                p0 += 1

        # Calculate the total number of issues
        total = p2 + p1 + p0

        # Avoid division by zero
        if total == 0:
            return 100  # No issues found, return the best score

        # Calculate the score based on the provided formula
        score = (1 - ((0.2 * p2 + 0.4 * p1 + p0) / total)) * 100
        

        return score

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
        data = []
        for violation in self.data['violations']:
            for node in violation['nodes']:
                data.append({
                    #'URL': violation.get('url', ''),
                    'ID': violation.get('id', ''),
                    'Impact': violation.get('impact', ''),
                    'Help': violation.get('help', ''),
                    'HTML': node.get('html', ''),
                    'Target': " | ".join(node.get('target', [])),
                    'Help URL': violation.get('helpUrl', '')
                })
    
        # Create the dataframe
        df = pd.DataFrame(data)
        return df

# Example usage
#json_file = 'path_to_your_json_file'  # Replace with your actual JSON file path
#report_viewer = AccessibilityReportViewer(json_file)
#accessibility_score = report_viewer.calculate_accessibility_score()
#print(f"Accessibility Score: {accessibility_score}%")

#critical_violations = report_viewer.extract_critical_violations()
#for violation in critical_violations:
    #print(violation)
