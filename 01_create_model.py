r"""
Create and calibrate a model object from the source file
"""


# External packages
import irispie as ir

# Internal modules
import file_structure as fs


# Create model object from source file

model = ir.Simultaneous.from_file(
    "model_files/closed_economy_qpm.model",
    linear=False,
    flat=False,
    description="Closed economy QPM"
)

# Assign parameters

# Direct way
model.assign_strict(
    # Steady-state parameteres,
    ss_rrs=0,
    ss_ad_cpi=2,
    ss_ad_y=1.5,
    # Dynamic parameters,
    c0_y_gap=0.75,
    c1_y_gap=0.10,
    c0_ad_cpi=0.55,
    c1_ad_cpi=0.10,
    c1_ad_cpi_ste=1,
    c2_ad_cpi_ste=0.1,
    c0_rs=0.75,
    c0_rrs_tnd=0.95,
    c1_mpr=4,
    c0_ad_y_tnd=0.95,
    # Stds for shocks,
    std_shk_ad_y_tnd=3,
    std_shk_y_gap=1.0,
    std_shk_ad_cpi=2.0,
    std_shk_rs=0.3,
    std_shk_ad_cpi_ste=0.1,
    std_shk_rrs_tnd=0.5,
    # Stds for measurement errors,
    std_shk_obs_y=0,
    std_shk_obs_cpi=0,
    std_shk_obs_rs=0,
)


# More structured way
parameters_db = ir.Databox.from_file("calibrate_parameters.db.py")
model.assign_strict(parameters_db)


# Print the parameters from within the model
parameters_assigned = model.get_parameters()
print("Parameters assigned to the model:")
print(parameters_assigned)


# Calculate steady state

model.solve_steady()
model.check_steady()


# Calculate steady state with y=1 and cpi=1

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

print("Steady-state values:")
print(steady_table)


# Calculate first-order solution matrices

model.solve_first_order()


# Save model object to pickle file

model.to_pickle_file(fs.MODEL_PICKLE_FILE)

