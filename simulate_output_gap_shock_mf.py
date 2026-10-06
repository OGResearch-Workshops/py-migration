
# Import packages we need
import irispie as ir


# Load the model object
model = ir.Simultaneous.from_pickle_file("pickle_files/model.pkl")


# Create a steady state databox
simulation_span = ir.qq(2025,1) >> ir.qq(2028,4)
db = model.build_steady_paths(simulation_span)

# Create a shock in the steady state databox
db["shk_y_gap"][ir.qq(2025,1)] = 1

# Run a simulation using the model and the databox
s = model.simulate(db, simulation_span)

s["rs"].plot()
