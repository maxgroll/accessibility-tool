# config/constants.py
import os

# basic path to data folder
DATA_DIRECTORY = "data"

# paths tu subfolders
LOGS_DIRECTORY = "logs"
ACCESSIBILITY_RESULTS_DIRECTORY = "accessibility_results"
# Full paths to subfolders
FULL_LOGS_DIRECTORY = os.path.join(DATA_DIRECTORY, LOGS_DIRECTORY)
FULL_ACCESSIBILITY_RESULTS_DIRECTORY = os.path.join(DATA_DIRECTORY, ACCESSIBILITY_RESULTS_DIRECTORY)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

CDNJS_AXE_API = "https://api.cdnjs.com/libraries/axe-core?fields=version"
AXE_CDN_LATEST = (
    "https://cdnjs.cloudflare.com/ajax/libs/axe-core/{version}/axe.min.js"
)