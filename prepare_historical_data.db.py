r"""
Transform raw FRED data into historical data
"""


import irispie as ir


# Monthly data - NTF

cpi_mm = 100 * ir.log(CPIAUCSL)
ip_mm = 100 * ir.log(INDPRO)
ppi_mm = 100 * ir.log(PPIFIS)
m1_mm = 100 * ir.log(M1SL)
wage_mm = 100 * ir.log(CES0500000003)

rs_mm = TB3MS
r5y_mm = GS5
r10y_mm = GS10
unr_mm = UNRATE


# Quarterly data - core model

y = 100 * ir.log(GDPC1)

cpi = ir.aggregate(CPIAUCSL, ir.QUARTERLY, method="mean", )
cpi = 100 * ir.log(cpi)

rs = ir.aggregate(TB3MS, ir.QUARTERLY, method="mean", )
r5y = ir.aggregate(GS5, ir.QUARTERLY, method="mean", )
r10y = ir.aggregate(GS10, ir.QUARTERLY, method="mean", )

