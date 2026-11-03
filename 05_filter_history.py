r"""
Run Kalman filter on the historical data, and set up initial conditions for the forecast
"""


# Import external packages
import irispie as ir

# Import internal modules
import file_structure as fs


model = ir.Simultaneous.from_pickle_file(fs.MODEL_PICKLE_FILE, )

model.assign_strict(
    std_shk_rs=3,
    std_shk_ad_cpi=1,
    std_shk_rrs_tnd=0.5,
)

model.check_steady()
model.solve_first_order()


# Load historical data from CSV file
hist_db = ir.Databox.from_csv(fs.HISTORICAL_DATA_FILE, )

# Create a new Databox with the observed data series for the Kalman filter
obs_db = hist_db.copy(
    source_names=("y", "rs", "cpi", ),
    # target_names=lambda n: f"obs_{n}",
    target_names=("obs_y", "obs_rs", "obs_cpi", ),
)


# Set up the filter span for the Kalman filter
start_filt = ir.qq(2010,1)
end_filt = ir.qq(2026,2)
filter_span = start_filt >> end_filt


# Run a plain vanilla Kalman filter on the observed data series, and return the
# filtered data series and additional information
kalman_db, info, = model.kalman_filter(
    obs_db, filter_span,
    return_info=True,
    rescale_variance=True,
)


# Run an alternative Kalman filter with a different standard deviation for the
# trend shock during COVID, and return the filtered data series and
# additional
std_db = ir.Databox(
    std_shk_ad_y_tnd=ir.Series(periods=ir.qq(2020,1,...,2020,4), values=10),
)

alt_kalman_db = model.kalman_filter(
    obs_db | std_db, filter_span,
    stds_from_data=True,
)


smooth_db = kalman_db["smooth_med"]
alt_smooth_db = alt_kalman_db["smooth_med"]

smooth_db["filter_span"] = ir.Series(periods=filter_span, values=1, )
smooth_db.to_csv_file(fs.FILTER_DATA_FILE, )


ch = ir.Chartpack(
    tiles=(2, 2),
    span=filter_span,
    show_legend=False,
)

f = ch.add_figure("Kalman filter", )
f.add_charts([
    "Output: y | y_tnd",
    "Output gap: y_gap",
    "Real interest rate: rrs | rrs_tnd",
    "Real interest rate gap: rrs_gap",
])

chart_db = ir.Databox.by_merging([smooth_db, alt_smooth_db])
ch.plot(chart_db)

