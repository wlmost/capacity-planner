"""
Application Constants
"""
from pathlib import Path

# Version
APP_VERSION = "0.1.0"
APP_NAME = "Kapazitäts- & Auslastungsplanner"
APP_ORG = "YourOrg"

# Paths
USER_DATA_DIR = Path.home() / ".capacity_planner"
DATABASE_PATH = USER_DATA_DIR / "data.db"
KEYS_DIR = USER_DATA_DIR / "keys"

# Database
DB_CONNECTION_NAME = "capacity_planner_main"

# UI
WINDOW_MIN_WIDTH = 1024
WINDOW_MIN_HEIGHT = 768

# Time Formats
TIME_FORMAT_COLON = "colon"  # 1:30
TIME_FORMAT_DECIMAL = "decimal"  # 1.5h

# Date Formats
DATE_FORMAT_ISO = "%Y-%m-%d"
DATETIME_FORMAT_ISO = "%Y-%m-%d %H:%M:%S"
