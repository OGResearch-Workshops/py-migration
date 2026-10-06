r"""
Run Kalman filter on the historical data, and set up initial conditions for the forecast
"""


import sys
import irispie as ir
import file_structure as fs


model = ir.Simultaneous.from_pickle_file(fs.MODEL_PICKLE_FILE, )

model.assign_strict(
    std_shk_rs=3,
    std_shk_ad_cpi=1,
    std_shk_rrs_tnd=0.5,
)

model.check_steady()
model.solve_first_order()


historical_db = ir.Databox.from_csv(fs.HISTORICAL_DATA_FILE, )

obs_db = historical_db.copy(
    source_names=("y", "rs", "cpi", ),
    target_names=lambda n: f"obs_{n}",
)

start_filt = ir.qq(2010,1)
# end_filt = ir.qq(2022,4)
end_filt = ir.qq(2025,4)
filter_span = start_filt >> end_filt

kalman_db, info, = model.kalman_filter(
    obs_db, filter_span,
    return_info=True,
    rescale_variance=True,
)

std_db = ir.Databox(
    std_shk_ad_y_tnd=ir.Series(periods=ir.qq(2020,1,...,2020,4), values=10),
)

k2 = model.kalman_filter(
    obs_db | std_db, filter_span,
    stds_from_data=True,
)


s = kalman_db["smooth_med"]
s2 = k2["smooth_med"]
s["filter_span"] = ir.Series(periods=filter_span, values=1, )
s.to_csv_file(fs.FILTER_DATA_FILE, )


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

ch.plot(ir.Databox.by_merging((s,s2)))




### multiplier_db = ir.Databox(
###     std_shk_obs_cpi=ir.Series(periods=ir.qq(2022,1)>>ir.qq(2022,4), values=0, )
### )
### 
### 
### std_db = ir.Databox(
###     std_shk_rs=10,
###     std_shk_ad_y_tnd=ir.Series(periods=ir.qq(2019,3)>>ir.qq(2021,1), values=10, )
### )
### 
### tv_stds = model.vary_stds(
###     multiplier_db=multiplier_db,
###     #std_db=std_db,
###     std_db=None,
###     span=filter_span,
### )
### 
### 
### filt_db, info, = model.kalman_filter(
###     obs_db, filter_span,
###     return_info=True,
###     rescale_variance=True,
###     prepend_initial=True,
### )
### s1 = filt_db["smooth_med"]
### 
### s = filt_db["smooth_med"]
### 
### tv_filt_db, tv_info = model.kalman_filter(
###     obs_db | tv_stds, filter_span,
###     return_info=True,
###     rescale_variance=True,
###     stds_from_data=True,
### )
### 
### tv_s = tv_filt_db["smooth_med"]
### 
### 
### std_scale = info["std_scale"]
### m_rescaled = model.copy()
### m_rescaled.rescale_stds(std_scale, )
### 
### _, info_rescaled = m_rescaled.kalman_filter(
###     obs_db, filter_span,
###     return_info=True,
###     rescale_variance=True,
### )
### 
