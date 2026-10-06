r"""
Create and calibrate a model object from the source file
"""


# External packages
import irispie as ir

# Internal modules
import file_structure as fs


model = ir.Simultaneous.from_file(
    "model_files/closed_economy_qpm.model",
    linear=False,
    flat=False,
    description="Closed economy QPM"
)


# Assign parameters
parameters_db = ir.Databox.from_file("calibrate_parameters.db.py")
print(parameters_db)

model.assign_strict(parameters_db)


# Calculate steady state

plan = ir.SteadyPlan(model)

plan.fix_level("y")
model.assign_strict(y=1)

plan.fix_level("cpi")
model.assign_strict(cpi=1)

model.solve_steady(plan=plan)
model.check_steady()

steady_table = model.create_steady_table(
    round_to=4,
    to_csv_file=fs.STEADY_TABLE_CSV_FILE,
)

print(steady_table)


# Calculate first-order solution matrices

model.solve_first_order()


# Save model object to pickle file
model.to_pickle_file(fs.MODEL_PICKLE_FILE)

