r"""
Read US data from St Louis Fred database
"""


# External packages
import macrotap as mt

# Internal modules
import file_structure as fs


# Download raw data from Fred

fred_codes = [
    #
    # Real Gross Domestic Product, Billions of Chained 2012 Dollars, Seasonally
    # Adjusted Annual Rate
    "GDPC1",
    #
    # Consumer Price Index for All Urban Consumers: All Items in U.S. City
    # Average, Not Seasonally Adjusted
    "CPIAUCNS",
    #
    # Consumer Price Index for All Urban Consumers: All Items, Seasonally
    # Adjusted
    "CPIAUCSL",
    #
    # 3-Month Treasury Bill: Secondary Market Rate
    "TB3MS",
    #
    # 5-Year Treasury Constant Maturity Rate
    "GS5",
    #
    # 10-Year Treasury Constant Maturity Rate
    "GS10",
    #
    # Civilian Unemployment Rate, Seasonally Adjusted
    "UNRATE",
    #
    # Industrial Production Index, Seasonally Adjusted
    "INDPRO", 
    #
    # M1 Money Stock, Seasonally Adjusted
    "M1SL",
    #
    # Producer Price Index by Industry: Final Demand: Goods, Seasonally Adjusted
    "PPIFIS",
    #
    # Average Hourly Earnings of Production and Nonsupervisory Employees: Total
    # Private, Seasonally Adjusted
    "CES0500000003",
]

fred_db = mt.from_fred(fred_codes, )


fred_db0 = fred_db.copy()

print(fred_db0)

# Fill in missing values in the CPI (government shutdown)
fred_db["CPIAUCSL"].fill_missing(method="log_linear", )
fred_db["CPIAUCNS"].fill_missing(method="log_linear", )
fred_db["UNRATE"].fill_missing(method="linear", )

print(fred_db)

# Save the raw FRED data to a CSV file
fred_db.to_csv_file(fs.FRED_DATA_FILE, )
