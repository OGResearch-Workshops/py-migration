r"""
Prepare historical data from raw FRED data
"""


# Import external packages
import irispie as ir

# Import internal modules
import file_structure as fs


# Load raw FRED data from CSV file
hist_db = ir.Databox.from_csv_file(fs.FRED_DATA_FILE)

# Capture the names of the original FRED data series before transforming data
fred_names = hist_db.get_names()


# Transform the raw FRED data into historical data with model-consistent naming

# Monthly data

hist_db["cpi_mm"] = 100 * ir.log(hist_db["CPIAUCSL"])
hist_db["ip_mm"] = 100 * ir.log(hist_db["INDPRO"])
hist_db["ppi_mm"] = 100 * ir.log(hist_db["PPIFIS"])
hist_db["m1_mm"] = 100 * ir.log(hist_db["M1SL"])
hist_db["wage_mm"] = 100 * ir.log(hist_db["CES0500000003"])

hist_db["rs_mm"] = hist_db["TB3MS"]
hist_db["r5y_mm"] = hist_db["GS5"]
hist_db["r10y_mm"] = hist_db["GS10"]
hist_db["unr_mm"] = hist_db["UNRATE"]

# Quarterly data

# hist_db.y = 100 * log(hist_db.GDPC1)
hist_db["y"] = 100 * ir.log(hist_db["GDPC1"])

hist_db["cpi"] = ir.aggregate(hist_db["CPIAUCSL"], ir.QUARTERLY, method="mean", )
hist_db["cpi"] = 100 * ir.log(hist_db["cpi"])

hist_db["rs"] = ir.aggregate(hist_db["TB3MS"], ir.QUARTERLY, method="mean", )
hist_db["r5y"] = ir.aggregate(hist_db["GS5"], ir.QUARTERLY, method="mean", )
hist_db["r10y"] = ir.aggregate(hist_db["GS10"], ir.QUARTERLY, method="mean", )


# Execute the preparation script to transform the raw FRED data into historical
# data
# hist_db.execute_file("prepare_historical_data.db.py")


# Remove the original FRED data series from the historical data database
hist_db.remove(fred_names)

# Print the historical data database to verify the transformations
print(hist_db)

# Save the historical data database to a CSV file
hist_db.to_csv_file(fs.HISTORICAL_DATA_FILE)

