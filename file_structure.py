r"""
Files and folders
"""


import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILES_DIR = os.path.join(THIS_DIR, "data_files", )
PICKLE_FILES_DIR = os.path.join(THIS_DIR, "pickle_files", )

STEADY_TABLE_CSV_FILE = os.path.join(DATA_FILES_DIR, "steady_table.csv", )
FRED_DATA_FILE = os.path.join(DATA_FILES_DIR, "fred_data.csv", )
HISTORICAL_DATA_FILE = os.path.join(DATA_FILES_DIR, "historical_data.csv", )
FILTER_DATA_FILE = os.path.join(DATA_FILES_DIR, "filter_data.csv", )

MODEL_PICKLE_FILE = os.path.join(PICKLE_FILES_DIR, "model.pkl", )


