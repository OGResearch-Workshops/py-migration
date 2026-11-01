# Iris Toolbox (Matlab) vs IrisPie (Python)

What changes in everyday modeling tasks

---

## 1. Scope and the short version

Both the Iris Toolbox and IrisPie are focused mainly on **structural
macroeconomic models**: models written in a model file, with a steady state, a
solution, simulations, filtering, and forecasts. But that is not the only
functionality. Both also provide:

* empirical time series models (VARs and related tools),
* data management (time series, dates, collections of series),
* charting and reporting.

This note is organized by **task** and covers the ones that come up in nearly
every project: the structural-model workflow, plus the data handling and charts
that every project touches. The workflow is the same in both languages; what
changes is the syntax around it, and a handful of habits that follow from
Python being a general-purpose language.

The Python snippets are adapted from the workshop scripts
(`01_create_model.py` to `07_simulate_floor.py`). For the broader picture of
the migration, see `m_to_py_migration.md`. In the snippets below, Matlab uses
the `name=value` option syntax, and `import irispie as ir` is assumed on the
Python side.


## 2. Vocabulary map

* `Model` &rarr; `Simultaneous`
* `Plan` &rarr; `SimulationPlan` (and `SteadyPlan` for the steady state)
* `tseries` / `Series` &rarr; `Series`
* struct (databank) &rarr; `Databox`
* `Explanatory` &rarr; `Explanatory` (and `Sequential`)
* `VAR` / `SVAR` &rarr; `RedVAR` / `StructVAR`
* `Chartpack` &rarr; `Chartpack` (interactive Plotly charts)


## 3. Task by task

### 3.1 Dates and ranges

```Matlab
startFilt = qq(2010,1);
endFilt = qq(2026,2);
filterRange = startFilt : endFilt;
```

```python
start_filt = ir.qq(2010, 1)
end_filt = ir.qq(2026, 2)
filter_span = start_filt >> end_filt
```

* Period constructors (`qq`, `mm`, `yy`, `ii`, ...) and period arithmetic
  (`start + 4`) work as before.
* A range written `a : b` becomes a **span** written `a >> b`.


### 3.2 Time series and databanks

```Matlab
d = databank.fromCSV("historical_data.csv");
d.shk_y_gap(qq(2020,1)) = 1;
databank.toCSV(d, "out.csv");
```

```python
db = ir.Databox.from_csv_file("data_files/historical_data.csv")
db["shk_y_gap"][ir.qq(2020, 1)] = 1
db.to_csv_file("data_files/out.csv")
```

* A databank is a plain struct; a `Databox` is a dictionary-like object. Look
  up series with `db["name"]`.
* Series are indexed **by period**.
* Functions on series live in the package: `100 * log(x)` becomes
  `100 * ir.log(x)`.
* **Copying is explicit** (see section 4): use `db.copy()`.
* A list of transformations can be kept in a `.db.py` file and run against a
  databox with `db.execute_file("prepare_historical_data.db.py")`.


### 3.3 The model file

The model file language is shared. The same blocks exist
(`!transition-variables`, `!transition-shocks`, `!parameters`,
`!transition-equations`, `!measurement-*`), as do the steady-state separator
`!!`, the `!for` and `!if` directives, `!log-variables` / `!all-but`,
`!substitutions`, `!autoswaps-*`, and `!preprocessor` / `!postprocessor`. Both
hyphens and underscores are accepted in keywords (`!transition-variables` or
`!transition_variables`).

At the time of writing we did not find these Matlab directives in the Python
parser: `!links`, `!dtrends`, `!ttrend`, `!import` / `!export`, `!switch`,
`!function`.

```Matlab
m = Model.fromFile( ...
    "closed_economy_qpm.model" ...
    , linear=false ...
);
```

```python
model = ir.Simultaneous.from_file(
    "model_files/closed_economy_qpm.model",
    linear=False,
    flat=False,
    description="Closed economy QPM",
)
```


### 3.4 Calibrate, steady state, solve

```Matlab
model = assign(model, p);
model = steady(model, fixLevel="y");
checkSteady(model);
model = solve(model);
```

```python
model.assign_strict(p)

plan = ir.SteadyPlan(model)
plan.fix_level("y")

model.solve_steady(plan=plan)
model.check_steady()
model.solve_first_order()
```

* **Methods modify the model in place.** There is no `m = ...`: the model
  object is updated by `assign_strict`, `solve_steady`, and
  `solve_first_order`. This is the most common porting trap.
* `assign_strict` raises an error on unknown names, which catches typos.
* Steady-state and solution steps are separate, explicitly named methods.
* Fixing a level or growth rate is done in Matlab through steady-state options
  (e.g. `FixGrowth=`) and in IrisPie through a `SteadyPlan` object.


### 3.5 Simulate

```Matlab
d = steadydb(m, 1:20);
d.shk_y_gap(1) = 1;
s = simulate(m, d, 1:20);
```

```python
sim_span = ir.ii(1) >> ir.ii(20)
db = model.build_steady_paths(sim_span)
db["shk_y_gap"][ir.ii(1)] = 1
sim_db = model.simulate(db, sim_span)
```

Choosing the method and solver:

```Matlab
s = simulate( ...
    m, d, range ...
    , method="stacked" ...
    , solver={"iris-newton", "maxIterations", 100} ...
);
```

```python
sim_db = model.simulate(
    db, sim_span,
    method="stacked_time",
    solver_settings={"step_tolerance": 100},
)
```

* Methods: `"firstOrder"`, `"stacked"`, `"period"` in Matlab; `"first_order"`,
  `"stacked_time"`, `"period_by_period"` in Python (`"stacked"` and `"period"`
  are accepted as aliases). `first_order` is the default in both.
* **Anticipated shocks have their own names.** In Matlab a shock `shk_x` is
  anticipated or not depending on the `anticipate=` option and on the plan. In
  IrisPie every shock `shk_x` has an anticipated twin `ant_shk_x`, and you put
  values in whichever you mean.
* `simulate` **prepends the input data to the output by default** in Python
  (`prepend_input=True`); in Matlab the default is `prependInput=false`.


### 3.6 Conditional forecasts with plans

```Matlab
p = Plan.forModel(m, fcastRange);
p = exogenize(p, tuneRange, "rs");
p = endogenize(p, tuneRange, ["shk_ad_cpi", "shk_y_gap"]);
s = simulate(m, d, fcastRange, plan=p);
```

```python
plan = ir.SimulationPlan(model, fcast_span)
plan.exogenize_anticipated(tune_span, "rs")
plan.endogenize_anticipated(tune_span, ["ant_shk_ad_cpi", "ant_shk_y_gap"])
sim_db = model.simulate(
    input_db, fcast_span,
    plan=plan,
)
```

* In Matlab the anticipation status of each name is a property of the plan,
  set with `anticipate(p, true, names)`. In IrisPie it is part of the **method
  name**: `exogenize_anticipated` / `exogenize_unanticipated`,
  `endogenize_anticipated` / `endogenize_unanticipated`, and
  `swap_anticipated` / `swap_unanticipated`. This is the clearest example of
  "explicit better than implicit".
* Shock names in the plan are the explicit ones (`ant_shk_...` or
  `shk_...`).


### 3.7 Kalman filter

```Matlab
[outDb, outModel, info] = kalmanFilter( ...
    m, obsDb, filterRange ...
    , unitRootInitials="fixedUnknown" ...
);
```

```python
kalman_db, info = model.kalman_filter(
    obs_db, filter_span,
    return_info=True,
    rescale_variance=True,
    diffuse_method="fixed_unknown",
)
smooth_db = kalman_db["smooth_med"]
```

* By default Matlab returns the smoothed median in a flat databank and also
  returns the (possibly updated) model. IrisPie returns one databox that holds
  several flavors of output (e.g. `smooth_med`), and the model is not
  returned.
* Option values are written in snake case: `approxDiffuse` /
  `fixedUnknown` become `approx_diffuse` / `fixed_unknown`.
* Shock standard deviations can come from the data
  (`stds_from_data=True`), as used in `05_filter_history.py`.


### 3.8 One forecast round, end to end

The workshop pipeline is the template: `04` prepares the data, `05` filters
the history and saves `filter_data.csv`, and `06` simulates forecasts from
that file. In Matlab the same sequence of steps applies, with the filtered
databank passed straight on to `simulate`.


### 3.9 Charts

```Matlab
ch = Chartpack( );
ch.Range = startDate : endDate;
add(ch, "Output gap: y_gap");
draw(ch, s);
```

```python
ch = ir.Chartpack(
    span=chart_span,
)
fig = ch.add_figure("Forecasts")
fig.add_charts([
    "Output gap: y_gap",
])
ch.plot(sim_db)
```

* The `"Caption: expression"` strings carry over.
* IrisPie adds a **figure** level: tiles are laid out per figure.
* Charts are interactive Plotly figures that open in the browser, rather than
  Matlab figures.


### 3.10 Saving and loading models

```Matlab
save("model.mat", "m");
load("model.mat");
```

```python
model.to_pickle_file("pickle_files/model.pkl")
model = ir.Simultaneous.from_pickle_file("pickle_files/model.pkl")
```

A pickle file belongs to the versions of the packages that created it. After
upgrading `irispie`, rebuild it from the model file (`01_create_model.py`).


## 4. Language-level habits to change

* **Methods, not functions.** `m = simulate(m, d, range)` becomes
  `model.simulate(d, span)`.
* **In-place updates.** Methods typically change the object and return nothing
  (section 3.4); Matlab code that reassigns (`m = steady(m)`) should not be
  translated literally.
* **Assignment by reference.** `b = a` does not copy; use `.copy()` to get an
  independent databox or model.
* **Keyword arguments** with snake-case names (`return_info=True`).
* **No scripts, only modules.** Each file has its own namespace, so shared
  values are imported (see `file_structure.py`).
* **Indexing:** plain Python lists start at 0, whereas series are indexed by
  period.


## 5. Coverage differences

Not yet available in IrisPie, as listed in the migration slides: estimation of
structural models (priors, system priors), nonlinear quasi-filtering, and
factor models.

At the time of writing we also found no direct equivalents of the Matlab
frequency-domain tools (`xsf`, `ffrf`, `ifrf`), `fevd`, the Beveridge-Nelson
decomposition, or `tilting`.

New on the Python side: interactive Plotly charts. In addition, the packages
are small and focused, and can be installed without a license server.


## 6. Porting checklist

1. Port the **model file** first; most of it should work unchanged. Check it
   against the list in section 3.3.
2. Port the **data** next: load the same data into a `Databox` and compare a
   few series against the Matlab databank.
3. Port the scripts **one task at a time**, in the order of section 3 (dates,
   data, model, steady state, simulate, filter, forecast).
4. Replace `m = f(m, ...)` patterns by in-place calls, and add `.copy()` where
   a separate version of an object is needed.
5. Compare **steady states and one simulation** against the Matlab results
   before going further.
6. Only then port charts and reports.
