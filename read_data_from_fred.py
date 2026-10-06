r"""
Read US data from St Louis Fred database
"""


import macrotap as mt
import irispie as ir
import file_structure as fs
import sys


# Download raw data from Fred

fred_codes = [
    "GDPC1", # Real Gross Domestic Product, Billions of Chained 2012 Dollars, Seasonally Adjusted Annual Rate
    "CPIAUCSL", # Consumer Price Index for All Urban Consumers: All Items, Seasonally Adjusted
    "TB3MS", # 3-Month Treasury Bill: Secondary Market Rate
    "UNRATE", # Civilian Unemployment Rate, Seasonally Adjusted
    "INDPRO", # Industrial Production Index, Seasonally Adjusted
    "M1SL", # M1 Money Stock, Seasonally Adjusted
    "PPIFIS", # Producer Price Index by Industry: Final Demand: Services, Seasonally Adjusted
    "CES0500000003", # Average Hourly Earnings of Production and Nonsupervisory Employees: Total Private, Seasonally Adjusted
]

fred_db = mt.from_fred(fred_codes, )

print(fred_db)

fred_db.to_csv_file(fs.FRED_DATA_FILE, )

sys.exit()


# Convert monthly to quarterly

fred_db["CPIAUCSL"].fill_missing(method="log_linear", )
fred_db["CPIAUCSL"].aggregate(ir.QUARTERLY, method="mean", )
fred_db["TB3MS"].aggregate(ir.QUARTERLY, method="mean", )


# Create model-consistent databox

historical_db = ir.Databox()
historical_db["y"] = 100 * ir.log(fred_db["GDPC1"])
historical_db["cpi"] = 100 * ir.log(fred_db["CPIAUCSL"])
historical_db["rs" ] = fred_db["TB3MS"]


# Save to a CSV data file

historical_db.to_csv_file(fs.HISTORICAL_DATA_FILE, )

