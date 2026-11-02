# Migrating Macroeconomic Models from Matlab to Python

This folder is a self-contained, hands-on tutorial. You will build, calibrate,
simulate, and use for forecasting a small **semi-structural, "QPM-style"
(Quarterly Projection Model) closed-economy model** of the US economy. All of
it is done in Python, with the **IrisPie** modeling package.

If you have worked with the **IRIS Toolbox in Matlab**, the logic is the same:
model files, steady states, first-order solutions, Kalman filtering, simulation
plans. Only the host language has changed. If you have never used IRIS,
that's fine too. Everything is introduced from the economics side first.

You do **not** need to be a Python programmer. Each guided script (`01` to
`07`) is a short, linear, top-to-bottom recipe of about 20 to 100 lines. You
will read and run them, change a number, and see what happens.

**Quick start.** Install the packages (see [Setup](#setup)), then run the
scripts in numerical order: `python 01_create_model.py`, then `02`, and so on
up to `07`. Script `01` must come first because it creates the solved model
that every later script loads.

---

## Contents

1. [What you will do](#what-you-will-do)
2. [The software stack](#the-software-stack)
3. [Setup](#setup)
4. [Folder map](#folder-map)
5. [The model](#the-model)
6. [The workshop scripts, step by step](#the-workshop-scripts-step-by-step)
7. [Key concepts](#key-concepts)
8. [Suggested experiments](#suggested-experiments)
9. [Python for Matlab users: a few gotchas](#python-for-matlab-users-a-few-gotchas)
10. [Known loose ends](#known-loose-ends-for-instructors)
11. [Further reading](#further-reading)

---

## What you will do

The scripts form a pipeline, roughly the workflow of a central-bank forecast
round, shrunk down to its essentials:

```
 model file ──► calibrate ──► steady state ──► first-order solution
 (text)                                               │
                                                      ▼
 FRED data ──► historical data ──► Kalman filter ──► forecasts & scenarios
 (download)    (transform)         (estimate gaps,    (baseline, flat-rate,
                                    trends, shocks)    zero-floor episodes)
```

By the end you will have:

- **written down** a model in a plain-text model file (not in Python code),
- **calibrated** its parameters and computed its **steady state**,
- **simulated** a demand shock and read the impulse responses,
- **downloaded** real US data (GDP, CPI, interest rates, and more) from FRED
  and turned it into model-ready series,
- **filtered** the history to back out unobservables: potential output, the
  output gap, the equilibrium real rate, and the structural shocks,
- **produced forecasts**, including conditional ones, such as "what would
  have to happen for the policy rate to stay flat for a year?",
- **stress-tested** the model with an adverse demand shock that pushes the
  nominal interest rate into the **zero lower bound**.

---

## The software stack

The workshop uses a small family of focused packages rather than one big
monolith. They are developed by OGResearch and are layered as follows:

```
  macrotap   fetch public data (FRED)      ┐
                                           ├──►  datapie   time series, dates,
  irispie    macroeconomic modeling  ──────┘                Databoxes, charts
```

| Package | What it does | Role in this workshop |
|---|---|---|
| **`datapie`** | Time-series and data management: dates and frequencies (`Period`, `Span`), time series (`Series`), collections of series (`Databox`), and charting (`Chartpack`). Built on `numpy`, `scipy`, and `plotly`. | The "spreadsheet" layer. Everything you load, transform, and plot lives in a `Databox`. |
| **`irispie`** | The modeling engine: model-file parser, steady-state solver, first-order (rational expectations) solution, Kalman filter and smoother, simulations with plans. It **re-exports all of `datapie`**. | Used in every modeling script as `import irispie as ir`. |
| **`macrotap`** | Quick access to public data providers, currently FRED. | Used once, in `03_read_data_from_fred.py`. |

Because `irispie` re-exports `datapie`, **one import is enough**.
`ir.Databox`, `ir.Series`, `ir.qq(2010, 1)`, and `ir.Chartpack` all come from
`import irispie as ir`.

Other packages in the family (not used here, shown for context) cover
Excel-based reporting (`cellport`), PDF reporting (`rephorm`), and a
time-series-oriented data store (`timescroll`). See `docs/our_packaging.canvas`.

**Licensing in one paragraph.** `datapie` and `macrotap` are MIT-licensed.
`irispie` is *source-available* under three coordinated licenses: the
**Community Edition** (`irispie-ce`) for individuals, for personal, educational
and other non-commercial use (this is what the workshop installs); the
**Registered Edition** for organizations after registering with OGResearch; and
a private edition for OGResearch internal use. If in doubt, write to
`irispie[at]ogresearch.com`.

---

## Setup

You need **Python 3.11 or newer** (the dev container uses 3.14).

### Option A: Dev container (recommended for the workshop)

Open the folder in VS Code and choose *Reopen in Container*. The configuration
in `.devcontainer/devcontainer.json` starts from a Python 3.14 image and
installs everything:

```
pip install 'irispie-ce>=0.80.2' ipython 'macrotap>=0.3.0'
```

### Option B: Your own virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install ipython                # optional, a nicer interactive prompt
```

`requirements.txt` pins the minimum versions of the two packages that matter:

```
irispie-ce >= 0.79.3
macrotap   >= 0.3.0
```

(`datapie` and the numerical dependencies, such as `numpy`, `scipy`, `plotly`,
`pandas`, and `neqs`, come in automatically.)

### Running a script

From the workshop folder (so that relative paths like `model_files/...` work):

```bash
python 01_create_model.py
```

Charts open in your web browser (they are interactive Plotly figures).
Alternatively, start `ipython` and run `%run 02_simulate_output_gap_shock.py`
to keep all objects in memory and poke at them afterwards.

---

## Folder map

```
.
├── 01_create_model.py                 Build model from file, calibrate, steady state, solve
├── 02_simulate_output_gap_shock.py    Impulse response to a demand shock
├── 03_read_data_from_fred.py          Download US data from FRED
├── 04_prepare_historical_data.py      Transform raw data into model variables
├── 05_filter_history.py               Kalman filter: gaps, trends, shocks
├── 06_simulate_forecasts.py           Baseline and conditional forecasts
├── 07_simulate_floor.py               Zero-lower-bound simulation
├── 08_filter_history_experiments.py   Instructor scratchpad (advanced, see notes)
│
├── model_files/
│   └── closed_economy_qpm.model       The model, in IRIS/IrisPie model-file language
├── calibrate_parameters.db.py         Parameter values and shock std devs
├── prepare_historical_data.db.py      Data transformations (log, aggregate, ...)
├── file_structure.py                  One place that defines all file paths
│
├── data_files/                        CSV inputs and outputs (committed)
│   ├── fred_data.csv                  Raw data as downloaded from FRED
│   ├── historical_data.csv            Transformed, model-ready history
│   ├── filter_data.csv                Kalman-filter output: the forecast starting point
│   └── steady_table.csv               Steady-state values of all variables
├── pickle_files/
│   └── model.pkl                      Saved, solved model (created by script 01; git-ignored)
│
├── docs/
│   ├── m_to_py_migration.md           Slides-style notes on moving from Matlab to Python
│   └── our_packaging.canvas           Diagram of the package family (Obsidian canvas)
├── sandbox/                           Your own scratch space (git-ignored)
├── .devcontainer/                     VS Code dev-container definition
├── requirements.txt
└── README.md
```

A few notes on the conventions:

- **Scripts are numbered in the order you should run them.** Each one reads
  what the previous ones wrote to disk, so you can restart from any point.
- **`.db.py` files** are not ordinary Python scripts. They are *databox
  scripts*: plain lists of assignments (`name = value`) that are executed
  *into* a `Databox`. Think of them as a text-file version of a struct of
  parameters (`calibrate_parameters.db.py`) or a list of data transformations
  (`prepare_historical_data.db.py`).
- **`file_structure.py`** collects all file locations in one place so that
  scripts never hard-code paths.
- **`model.pkl`** is a binary snapshot of the solved model. It is git-ignored,
  so after cloning the repository you must run `01_create_model.py` once to
  create it.
- **No internet?** The CSV files in `data_files/` are committed. After
  running `01`, you can skip script `03` and continue with `04` (or even
  directly with `05`).

---

## The model

The model is a small **gap model**: every key variable is decomposed into a
slow-moving *trend* (equilibrium, potential, steady state) and a *gap*
(deviation from the trend). It is the simplest member of the family of
models used for monetary policy analysis in many central banks. The full
source is in `model_files/closed_economy_qpm.model`; it fits on one screen.

### The five behavioral equations

Notation: `y` is 100 x log real GDP, `y_gap` the output gap, `ad_cpi`
quarterly inflation at an annual rate, `rs` the nominal short rate (%), and
`rrs` the real short rate. Shocks are written `shk_*`.

1. **Aggregate demand (IS curve).** The output gap is persistent and falls
   when the real interest rate rises above its trend:

   `y_gap = c0_y_gap * y_gap[-1] - c1_y_gap * rrs_gap + shk_y_gap`

2. **Phillips curve.** Inflation depends on its own past, on inflation
   expectations, and on the output gap:

   `ad_cpi = c0_ad_cpi * ad_cpi[-1] + (1 - c0_ad_cpi) * ad_cpi_ste + c1_ad_cpi * y_gap + shk_ad_cpi`

3. **Inflation expectations.** Model-consistent (forward-looking) expectations
   anchored at the inflation target, with an extra term that lets a binding
   zero floor feed into expectations:

   `ad_cpi_ste = c1_ad_cpi_ste * ad_cpi[+1] + (1 - c1_ad_cpi_ste) * ss_ad_cpi + shk_ad_cpi_ste + c2_ad_cpi_ste * (rs - rs_unc)`

4. **Monetary policy reaction function.** The central bank smooths the rate
   and reacts to expected year-on-year inflation three quarters ahead
   (`mpr`). The actual rate is the unconstrained rate **floored at zero**:

   `rs_unc = c0_rs * rs[-1] + (1 - c0_rs) * (ss_rrs + ss_ad_cpi + mpr) + shk_rs`
   `mpr = c1_mpr * (d4_cpi[+3] - ss_ad_cpi)`
   `rs = maximum(rs_unc, 0)`

5. **Real-rate and potential-growth trends.** Both are persistent AR(1)
   processes returning to their steady-state values:

   `rrs_tnd = c0_rrs_tnd * rrs_tnd[-1] + (1 - c0_rrs_tnd) * ss_rrs + shk_rrs_tnd`
   `ad_y_tnd = c0_ad_y_tnd * ad_y_tnd[-1] + (1 - c0_ad_y_tnd) * ss_ad_y + shk_ad_y_tnd`

Plus identities: `y = y_tnd + y_gap`, the Fisher equation
`rrs = rs - ad_cpi[+1]`, and `rrs = rrs_tnd + rrs_gap`.

Notation in the model file: `x[-1]` is the lag, `x[+1]` is the lead
(**expectations are model-consistent**), and `ad_x = 4*diff(x)` and
`d4_x = diff(x, -4)` are the annualized quarterly and year-on-year changes,
generated by a short `!for` loop at the bottom of the equation block.

### Anatomy of a model file

A model file is a plain text file with labeled sections:

| Section | Contents |
|---|---|
| `!transition_variables` | Endogenous variables of the structural model, each with a human-readable label (`"Log real GDP" y`) |
| `!transition_shocks` | The structural shocks (`shk_...`) |
| `!parameters` | Parameters to be calibrated |
| `!transition_equations` | The equations, with optional labels in quotes |
| `!measurement_variables` | Variables you observe in data (`obs_y`, `obs_rs`, `obs_cpi`, ...) |
| `!measurement_shocks` | Measurement errors (`shk_obs_...`) |
| `!measurement_equations` | The link between the model and the data |

Two features are worth pointing out to economists:

- **Steady-state equations after `!!`.** Many equations carry a second
  expression after `!!`, for example `ad_cpi = ... !! ad_cpi = ss_ad_cpi;`.
  This is the equation to use *in the steady state* when the dynamic
  equation does not pin it down. It lets the solver compute the
  balanced-growth path cleanly.
- **Anticipated shocks.** For every transition shock `shk_X`, the model
  automatically provides an **anticipated** twin `ant_shk_X`. It is known to
  agents in advance, which is how forward guidance and "tuned" forecasts work.

The separate `xxx` variable (`xxx = !for <range(0, 4)> !do + rs[+?] !end;`)
is a deliberate small demonstration of the `!for` loop and leads. It expands
into the sum of the current and next three values of `rs`. It plays no role in
the economics of the model.

### Calibration

All parameters live in `calibrate_parameters.db.py`:

| Group | Parameters |
|---|---|
| Steady state | `ss_rrs = 0`, `ss_ad_cpi = 2` (inflation target), `ss_ad_y = 1.5` (trend growth) |
| Persistence | `c0_y_gap = 0.75`, `c0_ad_cpi = 0.55`, `c0_rs = 0.75`, `c0_rrs_tnd = 0.95`, `c0_ad_y_tnd = 0.95` |
| Transmission | `c1_y_gap = 0.10` (real-rate effect on demand), `c1_ad_cpi = 0.10` (Phillips slope), `c1_mpr = 4` (policy response) |
| Expectations | `c1_ad_cpi_ste = 1` (fully forward-looking), `c2_ad_cpi_ste = 0.1` (zero-floor effect) |
| Shock sizes | `std_shk_*` for each shock; measurement errors on the observed series set to 0 |

These are **illustrative, not estimated**. Estimation of structural models
(along with nonlinear quasi-filtering and factor models) is on the IrisPie
roadmap (see `docs/m_to_py_migration.md`).

The resulting steady state (`data_files/steady_table.csv`) is: inflation 2%,
trend growth 1.5%, nominal rate 2%, real rate 0%, and zero gaps.

---

## The workshop scripts, step by step

### `01_create_model.py`: Build and solve the model

- Reads the model file with `ir.Simultaneous.from_file(...)`. "Simultaneous"
  is IrisPie's name for a system of simultaneous (i.e., structural,
  forward-looking) equations.
- Loads calibration from `calibrate_parameters.db.py` into a `Databox` and
  assigns it to the model with `assign_strict`. *Strict* means it raises an
  error if you try to assign a name that does not exist, which catches typos.
- Computes the **steady state** under a `SteadyPlan` that fixes the *levels*
  of `y` and `cpi` at 1 (a normalization, since log-levels of trending
  variables are otherwise not pinned down), then checks it and writes
  `steady_table.csv`.
- Computes the **first-order solution** (the matrices that map state and
  shocks to next-period variables under rational expectations).
- Saves the solved model to `pickle_files/model.pkl`, so that all later
  scripts start from it instead of rebuilding.

### `02_simulate_output_gap_shock.py`: Your first impulse response

- Loads the saved model.
- Builds a **steady-state databox** over periods 1 to 20 (integer periods, `ir.ii`;
  there are no calendar dates in a pure simulation).
- Sets `shk_y_gap = 1` in period 1: a one-standard-unit positive demand shock.
- Runs `model.simulate(...)` and plots the output gap, GDP growth, inflation,
  and nominal and real interest rates with a `Chartpack`.
- Note that `simulate` uses the **`first_order` method by default**: the
  linearized rational-expectations solution computed in script `01`. This is
  fast and exact for the linear part of the model, but it cannot see the zero
  floor (see script `07`).

You should see the textbook response: demand rises, inflation follows via the
Phillips curve, the central bank hikes, and the real rate gap works the gap
back to zero.

### `03_read_data_from_fred.py`: Download real data

- Uses `macrotap.from_fred(...)` to download 11 US series from the St. Louis
  Fed's FRED database: real GDP (`GDPC1`), CPI (two variants), 3-month T-bill
  (`TB3MS`), 5- and 10-year yields, unemployment, industrial production, M1,
  PPI, and hourly earnings.
- Fills missing observations (e.g., the CPI gaps caused by a government
  shutdown) by log-linear or linear interpolation with `fill_missing`.
- Saves everything to `data_files/fred_data.csv`. **This requires an internet
  connection**; the repository already contains a copy of the file.

### `04_prepare_historical_data.py`: From raw data to model variables

- Loads the raw CSV into a `Databox`, then **executes the databox script**
  `prepare_historical_data.db.py` against it. In that script the FRED series
  names (`GDPC1`, `CPIAUCSL`, ...) are simply variables:
  - quarterly core model variables: `y = 100 * ir.log(GDPC1)`, `cpi` (quarterly
    mean of monthly CPI, then log), `rs`, `r5y`, `r10y`, all aggregated from
    monthly to quarterly frequency with `ir.aggregate(..., method="mean")`;
  - monthly "non-core" variables (`cpi_mm`, `ip_mm`, `unr_mm`, ...) kept for
    reference.
- Removes the raw FRED names and saves `data_files/historical_data.csv`.

> Note the **mixed frequencies** in the CSV files. Quarterly and monthly
> series sit side by side in the same table under `__quarterly__` and
> `__monthly__` headers. `datapie` keeps track of the frequency of every
> series.

### `05_filter_history.py`: Kalman filter: estimating what you can't observe

The central step of any forecast round. GDP, inflation, and the interest
rate are observed. The output gap, potential output, the equilibrium real
rate, and the structural shocks are not. The **Kalman filter and smoother**
infer them by combining the model with the data.

- Copies `y`, `rs`, `cpi` into `obs_y`, `obs_rs`, `obs_cpi` (the names the
  measurement equations expect).
- Sets standard deviations of the shocks (`std_shk_rs`, `std_shk_ad_cpi`,
  `std_shk_rrs_tnd`). These determine how the filter *attributes* surprises
  to shocks: a large shock std means "this shock is a likely culprit".
- Runs `model.kalman_filter(...)` over **2010Q1 to 2026Q2**.
- Runs an **alternative filter** in which the std of the potential-growth shock is
  temporarily set to 10 in 2020 (`stds_from_data=True`), letting
  potential output move more during the pandemic year. Comparing the
  two shows how strongly such judgmental choices shape the estimated gap.
- Stores the smoothed estimates (including a `filter_span` indicator that
  marks where the history ends) in `data_files/filter_data.csv`. **This file
  is the jumping-off point for all forecasts.**
- Plots output vs. potential, the output gap, the real rate vs. its trend, and
  the real rate gap.

### `06_simulate_forecasts.py`: Baseline and conditional forecasts

Starting from the end of the filtered history, forecast **16 quarters** ahead
(`fcast_span`). Three variants are set up:

- **Forecast 0: hands-free.** No judgment: the model runs from the
  filtered starting point.
- **Forecast 1: flat policy rate.** *What macro conditions would be
  consistent with the nominal rate held constant for the next four
  quarters?* This is done with a **`SimulationPlan`**: the rate `rs` is
  *exogenized* (pinned to its last value) for four quarters, and, in
  exchange, two anticipated shocks (`ant_shk_ad_cpi`, `ant_shk_y_gap`) are
  *endogenized*, meaning they become unknowns solved to make it happen.
- **Forecast 2: tighter Phillips curve.** Same conditioning, but with a
  smaller std for the inflation shock. Since the inflation shock is "more
  expensive" to use, more of the adjustment must come from the output gap.

The chart compares the forecasts with the steady state and shades the
forecast window. In the version as committed only forecast 0 is plotted: the
line that merges all three is commented out. Un-comment it (it is the line
right below) to see all of them.

### `07_simulate_floor.py`: The zero lower bound

- Applies a **severe negative demand shock** (`shk_y_gap = -3` for four quarters)
  over a 40-period horizon.
- Simulates it twice, with two different methods:
  - the default **`first_order`** method, which uses the linearized solution
    and therefore **ignores the zero floor**; and
  - the **`stacked_time`** method, which solves the original non-linear
    equations jointly over the whole path, and therefore **enforces the
    floor** (a loose solver tolerance is passed to help it converge).
- Plots the output gap, inflation, the actual nominal rate `rs`, and the
  **unconstrained** rate `rs_unc` (what the policy rule would call for if
  negative rates were possible), with both simulations on the same charts.
  Comparing them shows what the floor does to the dynamics. In the
  `stacked_time` run, the distance between `rs` and `rs_unc` is a shadow-rate
  measure of the policy-space shortfall.

### `08_filter_history_experiments.py`: Instructor scratchpad

An advanced script used to exercise the more exotic corners of the Kalman
filter and simulation machinery: multiple model **variants** (parallel
parameter sets), diffuse initial conditions, shocks and std devs supplied in
the data, **shock multipliers**, and plans that **swap** endogenous and
exogenous variables. It is **not** part of the guided path and is not expected
to run cleanly from top to bottom (see [Known loose ends](#known-loose-ends-for-instructors)).

---

## Key concepts

A short glossary of the vocabulary you'll meet in the scripts, in economic
terms.

**Period, Span.** `ir.qq(2010, 1)` is 2010Q1. `ir.ii(1)` is integer period 1
(for simulations without calendar dates). `start >> end` builds a **span**
(range of periods). `period + 4` is a year later.

**Series.** A time series: values attached to periods, with a frequency.
Index it with periods: `series[ir.qq(2020, 1)]`. Missing values are `NaN`.

**Databox.** A named collection of series (and scalars), essentially a
dictionary that maps names to time series. A databox is both the *input*
(historical data, shocks, assumptions) and *output* (simulation results,
filtered estimates) of every model operation, and it can be saved to and
loaded from CSV. Two databoxes can be merged (`ir.Databox.by_merging([...])`)
for plotting several scenarios on one chart.

**Chartpack.** A figure layout: you list the variables (written as
`"Label: name"`) and it draws the tiles. Pass in a databox to plot. Several
databoxes merged with the same names appear as several lines in each tile.

**Steady state.** The balanced-growth path the model returns to when no
shocks hit. `build_steady_paths(span)` creates a databox of steady-state
paths: the natural starting point for any simulation.

**First-order solution.** The linear (in deviations) rational-expectations
solution around the steady state. Computed once and reused. It is what the
default `first_order` simulation method uses. Non-linearities, such as the
zero floor, are only respected by the other methods (`stacked_time`,
`period_by_period`), which work with the original equations.

**Anticipated vs. unanticipated shocks.** `shk_X` is a surprise: it hits
and agents learn of it only when it occurs. `ant_shk_X` is known in advance:
agents react today to a shock that materializes later. Anticipated shocks
are what forecasters use to "tune" paths.

**Simulation plan.** A recipe that changes *which variables are exogenous*
for a given simulation: you **exogenize** a variable (set it to a value of
your choosing) and **endogenize** a shock (let the model determine the
shock needed to achieve it). This is the model-based equivalent of a
forecaster's judgmental adjustment, and the basis of conditional forecasts,
scenarios, and policy-rule experiments.

**Kalman filter and smoother.** The way to turn data into model states and
shocks when some model variables are unobserved. The output databox has
several flavors; the scripts use `smooth_med` (the smoothed median estimate).
The *std* of each shock is the key setting that governs the attribution of
surprises (see script `05`).

**Variants.** A model object can hold several parameterizations at once.
`expand_num_variants(2)` (script `08`) duplicates it so that variant-specific
data can be run in parallel.

---

## Suggested experiments

These are not part of the repository's scripts, just ideas for working
through in the workshop. Copy a script into `sandbox/` (git-ignored), change
it, and watch what happens.

1. **Policy aggressiveness.** In `calibrate_parameters.db.py`, raise `c1_mpr`
   from 4 to 8 and re-run `01` and `02`. How does the response of inflation
   and output change?
2. **Flatter vs. steeper Phillips curve.** Change `c1_ad_cpi` (0.10) to 0.05
   and 0.30. Compare the inflation response to a demand shock.
3. **Less forward-looking expectations.** Set `c1_ad_cpi_ste` to 0.5 or 0
   (at 0, expectations are simply anchored at the inflation target). What
   happens to the persistence of inflation?
4. **A cost-push shock.** In script `02`, shock `shk_ad_cpi` instead of
   `shk_y_gap`. What is the trade-off the central bank faces?
5. **Forward guidance.** In script `06`, extend `tune_span` from 4 to 8
   quarters. How much does the output gap have to overshoot?
6. **Filter judgment.** In script `05`, change the std of the
   potential-growth shock for another episode (e.g., 2008-09) and compare
   the implied output gaps.
7. **The floor.** In script `07`, make the shock smaller, larger, or
   longer. How long does the economy stay at the floor in the `stacked_time`
   run? What does the `rs - rs_unc` gap look like?
8. **Use fresher data.** Re-run `03` to `06` after a new FRED release and
   extend `end_filt` in script `05`.

---

## Python for Matlab users: a few gotchas

These are also touched on in `docs/m_to_py_migration.md`.

- **There is no "script" in the Matlab sense.** A `.py` file runs top to
  bottom, but each file has its *own* namespace. Variables don't leak between
  files unless you `import` them (see how scripts import `file_structure as fs`).
- **Indexing starts at 0** for plain Python lists and arrays; but `datapie`
  series are indexed by *periods*, so you rarely need integer positions.
- **Assignment is by reference.** `b = a` does not copy. Both names point to
  the same object. Use `.copy()` (databoxes and models have it) when you
  want an independent version. That is why you see `filter_db.copy()` before
  every forecast variant in `06`.
- **Functions vs. methods.** You'll mostly call *methods* on objects:
  `model.simulate(...)`, `db.to_csv_file(...)`; in Matlab you would write
  `simulate(m, ...)`.
- **Named arguments** everywhere: `model.simulate(db, span, plan=plan)`.
  Order matters only for the first one or two arguments.
- **Whitespace matters.** Indentation defines blocks. This workshop's scripts
  barely use blocks, so it won't hurt you much.
- **Where is my workspace?** Python has no single built-in equivalent. VS
  Code, Spyder, JupyterLab, and IPython are all fine. Pick one and stay with it.

---

## Known loose ends (for instructors)

An honest list of things to know before running the workshop:

- **`08_filter_history_experiments.py` is a scratchpad** and will not run as
  committed: it reads `data_files/dates.json` (not in the repository), calls
  `sys.exit()` without importing `sys`, and references an undefined `kf1_db`
  in dead code after the first exit. Treat it as a menu of API examples,
  not a tutorial step.
- **Two spellings of one method.** Script `05` calls
  `ir.Databox.from_csv(...)` while the others call `from_csv_file(...)`. They
  are aliases, so this works, but participants may wonder which to use.
- **Version drift.** `requirements.txt` asks for `irispie-ce >= 0.79.3`; the dev
  container installs `irispie-ce >= 0.80.2`. The local development
  environment inside `.venv.nosync` uses editable installs of the packages
  from sibling source folders (`irispie-de` 0.80.1, `datapie` 0.7.1,
  `macrotap` 0.3.0). For a workshop, pin everyone to the same versions.
- **`ipython` is not in `requirements.txt`**, only in the dev container
  command. Install it separately if you want an interactive prompt.
- **Cosmetic:** the chart legend in `06` has a typo ("Forecaast 1"), and an
  `xxx` row appears in the steady table and the filter output. It is the
  `!for`-loop demo variable, not an error.
- **Data are vintage-dependent.** FRED revises history, so a fresh run of
  `03` will give slightly different numbers than the committed CSVs, and
  the filter end date in `05` (2026Q2) must be adjusted as new quarters appear.
- **Calibration is illustrative**, not estimated. Don't read policy
  conclusions into the exact numbers.

---

## Further reading

- **IrisPie documentation:** https://iris-solutions-team.github.io/irispie-pages
- **IrisPie tutorials:** https://iris-solutions-team.github.io/irispie-tutorials
- **IrisPie (community edition) source and issues:** https://github.com/iris-solutions-team/irispie-ce
- **DataPie documentation:** https://iris-solutions-team.github.io/datapie-pages
- **MacroTap documentation:** https://iris-solutions-team.github.io/macrotap-pages
- **Why we are moving from Matlab to Python:** `docs/m_to_py_migration.md`
- **The package family at a glance:** `docs/our_packaging.canvas`

For background on this class of models, look for introductions to
*"quarterly projection models"* and the *"gap model"* approach to monetary
policy analysis in the literature of central-bank modeling.
