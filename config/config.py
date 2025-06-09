# data/config.py

import logging
import os
from datetime import datetime

from .constants import FULL_ACCESSIBILITY_RESULTS_DIRECTORY, FULL_LOGS_DIRECTORY


def setup_logging() -> None:
    """
    Sets up the logging system with both a main log file and a session-specific log file.
    """
    # Main log
    main_log_file_path = os.path.join(FULL_LOGS_DIRECTORY, "main_debug.log")

    # Session logs
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    session_log_file_name = f"session_debug_{timestamp}.log"
    session_log_file_path = os.path.join(FULL_LOGS_DIRECTORY, session_log_file_name)

    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(levelname)s %(message)s',
                            handlers=[
                                logging.FileHandler(main_log_file_path),  # Schreibt in die Haupt-Log-Datei
                                logging.FileHandler(session_log_file_path),  # Schreibt in die session-spezifische Log-Datei
                                logging.StreamHandler()  # Schreibt in die Konsole
                            ])

def setup_directories() -> None:
    """
    Creates the necessary directories for logs and accessibility results if they don't already exist.
    """
    os.makedirs(FULL_LOGS_DIRECTORY, exist_ok=True)
    os.makedirs(FULL_ACCESSIBILITY_RESULTS_DIRECTORY, exist_ok=True)