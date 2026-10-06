r"""
Simulate a demand shock that drive the nominal rate to the zero floor
"""


import irispie as ir
import file_structure as fs


m = ir.Simultaneous.from_pickle_file(fs.MODEL_PICKLE_FILE, )


simulation_start = ir.ii(1)
simulation_end = ir.ii(40)
simulation_span = simulation_start >> simulation_end
chart_span = simulation_start-1 >> simulation_end

d = m.build_steady_paths(simulation_span, )
d["shk_y_gap"][simulation_start >> simulation_start+3] = -2

s0, info0 = m.simulate(
    d, simulation_span,
    return_info=True,
)

s1, info1 = m.simulate(
    d, simulation_span,
    return_info=True,
    method="stacked_time",
    solver_settings={"step_tolerance": 100, },
)

s = ir.Databox.by_merging((s0, s1), )

ch = ir.Chartpack(span=chart_span, )
fig = ch.add_figure("Adverse demand shock")
fig.add_charts((
    "Output gap: y_gap",
    "Inflation: ad_cpi",
    "Nominal interest rate: rs",
    "Unconstrained nominal interest rate: rs_unc",
    "Real interest rate: rrs",
))

ch.plot(s, )

