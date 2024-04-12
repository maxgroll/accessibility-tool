# data/constants.py
import os
# basic path to data folder
DATA_DIRECTORY = "data"

# paths tu subfolders
LOGS_DIRECTORY = "logs"
ACCESSIBILITY_RESULTS_DIRECTORY = "accessibility_results"
# Full paths to subfolders
FULL_LOGS_DIRECTORY = os.path.join(DATA_DIRECTORY, LOGS_DIRECTORY)
FULL_ACCESSIBILITY_RESULTS_DIRECTORY = os.path.join(DATA_DIRECTORY, ACCESSIBILITY_RESULTS_DIRECTORY)

