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


hist_db = ir.Databox.from_csv(fs.HISTORICAL_DATA_FILE, )

obs_db = hist_db.copy(
    source_names=("y", "rs", "cpi", ),
    target_names=lambda n: f"obs_{n}",
    # target_names=("obs_y", "obs_rs", "obs_cpi", ),
)

start_filt = ir.qq(2010,1)
end_filt = ir.qq(2026,2)
filter_span = start_filt >> end_filt

kalman_db, info, = model.kalman_filter(
    obs_db, filter_span,
    return_info=True,
    rescale_variance=True,
)

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

