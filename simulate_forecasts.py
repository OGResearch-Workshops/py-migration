r"""
Simulate forecast scenarios
"""

import sys
import irispie as ir
import file_structure as fs


model = ir.Simultaneous.from_pickle_file(fs.MODEL_PICKLE_FILE, )
filter_db = ir.Databox.from_csv_file(fs.FILTER_DATA_FILE, )

history_end = ir.qq(2025,4)
forecast_start = history_end + 1
forecast_end = history_end + 4*4
forecast_span = forecast_start >> forecast_end
chart_span = forecast_start-4*10 >> forecast_end

steady_db = model.build_steady_paths(chart_span, )



# Forecast 0
# Hands-free forecast with no adjustments

input_db0 = filter_db.copy()

s0 = model.simulate(
    input_db0, forecast_span,
)



# Forecast 1
# What macro conditions (output gap, inflation) would be consistent with a flat
# nominal interest rate path?

tune_span = forecast_start >> forecast_start+3
p1 = ir.SimulationPlan(model, forecast_span, )
p1.exogenize_anticipated(tune_span, "rs", )
p1.endogenize_anticipated(tune_span, ["ant_shk_ad_cpi", "ant_shk_y_gap", ], )

input_db1 = filter_db.copy()
input_db1["rs"][tune_span] = input_db1["rs"][history_end]


s1 = model.simulate(
    input_db1, forecast_span,
    plan=p1,
)



# Forecast 2
# Same as forecast 1, but with a tighter Phillips curve (lower std for the shock
# to inflation), meaning the output gap shocks would have to do more work to
# achieve the same nominal interest rate path.

tune_span = forecast_start >> forecast_start+3
p2 = ir.SimulationPlan(model, forecast_span, )
p2.exogenize_anticipated(tune_span, "rs", )
p2.endogenize_anticipated(tune_span, ["ant_shk_ad_cpi", "ant_shk_y_gap", ], )

input_db2 = filter_db.copy()
input_db2["rs"][tune_span] = input_db2["rs"][history_end]
input_db2["std_shk_ad_cpi"][tune_span] = 0.5

s2 = model.simulate(
    input_db2, forecast_span,
    plan=p2,
    stds_from_data=True, # unnecessary since this is the default behavior
)



# Plot the forecasts

ch = ir.Chartpack(
    tiles=(3,3),
    span=chart_span,
    highlight=forecast_span,
    legend=["Forecast 0", "Forecaast 1", "Forecast 2", "Steady state", ],
)

f = ch.add_figure("Forecasts", )
f.add_charts([
    "Output, Q/Q PA: ad_y",
    "Potential output, Q/Q PA: ad_y_tnd",
    "Output gap, %: y_gap",
    "CPI, Q/Q PA: ad_cpi",
    "Nominal interest rate: rs",
    "Real interest rate: rrs",
    "Ant shock to output_gap: ant_shk_y_gap",
    "Ant shock to inflation: ant_shk_ad_cpi",
    "Ant shock to nominal interest rate: ant_shk_rs",
])

chart_db = ir.Databox.by_merging([s0, s1, s2, steady_db, ])

ch.plot(chart_db, )

