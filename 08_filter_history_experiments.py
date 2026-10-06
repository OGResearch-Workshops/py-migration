
##

# Import standard and external packages
import numpy as np
import json as js
import irispie as ir


# Import internal modules
import file_structure as fs


m = ir.Simultaneous.from_pickle_file(fs.MODEL_PICKLE_FILE, )

print(m.get_parameters())


print(m.get_stds())


##


filt_db = ir.Databox.from_sheet(
    fs.FILTER_DATA_FILE,
    date_creator=ir.Period.from_iso_string,
)

hist_db = ir.Databox.from_sheet(
    fs.HISTORICAL_DATA_FILE,
    date_creator=ir.Period.from_iso_string,
)

obs_db = filt_db.copy(source_names=lambda n: n.startswith("obs_"), )

# alt_filt_db = ir.Databox.from_sheet(
#     "data_files/alt_filt_data.csv",
#     date_creator=ir.Period.from_iso_string,
# )
# 
# filt_db = alt_filt_db


with open("data_files/dates.json", "rt") as f:
    dates = js.load(f, )

start_filt = ir.Period.from_iso_string(dates["start_filt"], frequency=4, )
end_filt = ir.Period.from_iso_string(dates["end_filt"], frequency=4, )
filt_span = start_filt >> end_filt
ext_filt_span = start_filt >> end_filt + 10
num_filt_periods = len(filt_span)

##

# filt_db["ant_shk_y_gap"] = ir.Series(periods=filt_span, values=np.random.normal(size=len(filt_span)), )
# filt_db["ant_shk_diff_cpi"] = ir.Series(periods=filt_span, values=np.random.normal(size=len(filt_span)), )

# diffuse_method = "approx_diffuse"
diffuse_method = "fixed_unknown"

mm = m.copy()
mm.expand_num_variants(2, )

in1_db = hist_db.copy(target_names=lambda n: "obs_" + n, )
in1_db.pop("obs_diff_cpi")
in1_db.pop("obs_diff_y")

in1_db["ant_shk_diff_cpi"] = ir.Series(
    periods=filt_span,
    values=[0, np.random.normal(size=num_filt_periods), ],
    num_variants=2,
)

in1_db["shk_diff_cpi"] = ir.Series(
    periods=filt_span,
    values=[0, np.random.normal(size=num_filt_periods), ],
    num_variants=2,
)

in1_db["std_shk_diff_cpi"] = ir.Series(
    periods=filt_span,
    values=[None, 2+2*np.random.uniform(size=num_filt_periods), ],
    num_variants=2,
)

# in1_db["std_shk_obs_y"] = ir.Series(dates=ir.qq(2021,1), values=10, )
in1_db["std_shk_obs_y"] = 10


kf1_out = mm.kalman_filter(
    in1_db, filt_span,
    stds_from_data=True,
    shocks_from_data=True,
    prepend_initial=True,
    append_terminal=True,
    diffuse_method=diffuse_method,
)

smooth1_db = kf1_out.smooth_med


sim1_in_db = smooth1_db

sim1_db = mm.simulate(
    smooth1_db, filt_span,
)



## Shock multipliers

mult_db = ir.Databox()
mult_db["std_shk_obs_y"] = ir.Series(dates=ir.qq(2020,1,...,2022,4), values=314, )
mult_db["std_shk_diff_cpi"] = 100

out = m.multiply_stds(mult_db, None, filt_span, )


##

sim2_in_db = smooth1_db.shallow()
# del sim2_in_db["ant_shk_diff_cpi"]
del sim2_in_db["shk_y_gap"]

sim2_db = mm.simulate(
    sim2_in_db, filt_span,
)


sim3_in_db = sim2_in_db
plan3 = ir.SimulationPlan(mm, filt_span, )
plan3.swap_anticipated(filt_span, ("diff_cpi", "ant_shk_diff_cpi"), )
plan3.swap_unanticipated(filt_span, ("y_gap", "shk_y_gap"), )


sim3_db, sim3_info = mm.simulate(
    sim3_in_db, filt_span,
    plan=plan3,
    return_info=True,
)



sys.exit()

##

out2, kinfo2 = m.kalman_filter(
    filt_db, filt_span,
    stds_from_data=False,
    shocks_from_data=False,
    prepend_initial=True,
    diffuse_method="approx_diffuse",
)

sim2, sinfo2 = m.simulate(
    out2.smooth_med, filt_span,
    shocks_from_data=True,
)

out3, kinfo3 = m.kalman_filter(
    filt_db, ext_filt_span,
    stds_from_data=False,
    shocks_from_data=False,
    prepend_initial=True,
    diffuse_method="approx_diffuse",
    diffuse_scale=1e8,
)

sim3, sinfo3 = m.simulate(
    out3.smooth_med, ext_filt_span,
    shocks_from_data=True,
)


out4, kinfo4 = m.kalman_filter(
    filt_db, filt_span,
    stds_from_data=True,
    shocks_from_data=True,
    prepend_initial=False,
    diffuse_method=diffuse_method,
)

sim4, sinfo4 = m.simulate(out4.smooth_med, filt_span, )

names = m.get_names(kind=ir.TRANSITION_VARIABLE, )
med4 = out4.smooth_med.copy(source_names=names, )
std4 = out4.smooth_std.copy(source_names=names, )


med4.to_sheet(
    "data_files/python_smooth_med.csv",
    description_row=False,
    date_formatter=ir.Period.to_iso_string,
)

std4.to_sheet(
    "data_files/python_smooth_std.csv",
    description_row=False,
    date_formatter=ir.Period.to_iso_string,
)

kal1 = kf1_db.smooth_med.copy()
kal2 = out2.smooth_med.copy()

K = 10

p = ir.SimulationPlan(m, filt_span, )
# p.swap_unanticipated(start_filt, ("y_gap", "shk_y_gap"), )
# p.exogenize_unanticipated(start_filt+K, "y_gap")
# p.endogenize_unanticipated(start_filt+K, "shk_y_gap")

p.swap_anticipated(start_filt+3, ("y_gap", "ant_shk_y_gap"), )
p.swap_anticipated(start_filt+5, ("y_gap", "ant_shk_y_gap"), )
p.endogenize_anticipated(start_filt+2, "ant_shk_y_gap")
# p.swap_anticipated(start_filt+3, ("diff_cpi", "ant_shk_diff_cpi"), )

input_db4 = out2.smooth_med.copy()
input_db4["y_gap"][start_filt+3] = 10
input_db4["y_gap"][start_filt+5] = -10

sim4, sinfo4 = m.simulate(
    input_db4,
    filt_span,
    plan=p,
    split_frames=False,
)

print(sim4["ant_shk_y_gap"][start_filt+2>>start_filt+5])

resim4, *_ = m.simulate(sim4, filt_span, )

input_db5 = input_db4.copy()
input_db5["std_ant_shk_y_gap"] = ir.Series()
input_db5["std_ant_shk_y_gap"][start_filt+2] = 10

sim5, sinfo5 = m.simulate(
    input_db5,
    filt_span,
    plan=p,
    split_frames=False,
)

print(sim5["ant_shk_y_gap"][start_filt+2>>start_filt+5])

sys.exit(0)

sim3, sinfo3 = m.simulate(
    input_db3,
    filt_span,
    plan=p,
    split_frames=True,
)

resim3, *_ = m.simulate(
    sim3,
    filt_span,
    shocks_from_data=True,
)

sys.exit(0)

sim2, sinfo2 = m.simulate(
    out2.smooth_med,
    filt_span,
)

sim2, sinfo2 = m.simulate(
    out2.smooth_med,
    filt_span,
)



