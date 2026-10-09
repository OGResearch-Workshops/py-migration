
# Import packages we need
import irispie as ir


# Load the model object
model = ir.Simultaneous.from_pickle_file("pickle_files/model.pkl")


sim_start = ir.ii(1)
sim_end = ir.ii(20)
sim_span = sim_start >> sim_end
chart_span = sim_start-4 >> sim_end

# Create a steady state databox
db = model.build_steady_paths(sim_span)


# Create a shock in the steady state databox
db["shk_y_gap"][sim_start] = 1

# Run a simulation using the model and the databox
sim_db = model.simulate(db, sim_span)


# chart_db = sim_db

chart_db = ir.Databox.by_merging( [sim_db, db] )

ch = ir.Chartpack(
    tiles=(2, 3),
    span=chart_span,
    show_legend=False,
)

f = ch.add_figure("GDP gap shock", )
f.add_charts([
    "Real GDP gap: y_gap",
    "Real GDP growth: ad_y",
    "Inflation, Q/Q PA: ad_cpi",
    "Nominal interest rate: rs",
    "Real interest rate: rrs",
])

ch.plot(chart_db)

