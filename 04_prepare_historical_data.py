r"""
Prepare historical data from raw FRED data
"""


# Import external packages
import irispie as ir

# Import internal modules
import file_structure as fs


# Load raw FRED data from CSV file
hist_db = ir.Databox.from_csv_file(fs.FRED_DATA_FILE)

# Capture the names of the FRED data series before executing the preparation
# script
fred_names = hist_db.get_names()

# Execute the preparation script to transform the raw FRED data into historical
# data
hist_db.execute_file("prepare_historical_data.db.py")

# Remove the original FRED data series from the historical data database
hist_db.remove(fred_names)

# Print the historical data database to verify the transformations
print(hist_db)

# Save the historical data database to a CSV file
hist_db.to_csv_file(fs.HISTORICAL_DATA_FILE)

