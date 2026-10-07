
# Migrating from Matlab to Python

`.m` &rarr; `.py`

---

### Why away from Matlab

* Cost of Matlab licenses

* New hires increasingly arrive knowing Python (and R), not Matlab

* Closed, vendor-controlled ecosystem

* Reproducible, license-free deployment: servers, CI, and containers need no
  license to be provisioned (this workshop itself runs in a dev container)


---

### Why Python

* Widely used, scriptable, non-compiled, general-purpose language

* Mature numerical arrays and linear algebra (`numpy`, `scipy`)

* Business continuity:

  * no dependence on a single vendor

  * a long track record: Python has been around for over 30 years, whereas
    younger platforms (e.g. Julia) carry a greater risk of being abandoned,
    discontinued, or fading away

* Our choice was between Python and Julia; we chose Python for its longevity,
  larger ecosystem, and wider familiarity among our users


---

### What's ready

* Our own ecosystem of packages: `irispie` (source-available), `datapie`,
  `rephorm`, `macrotap` (MIT)

* Modeling package(s) replicating and extending the functionality of the Iris
  Toolbox, most importantly structural models, sequantial models, and empirical
  time series models

* Packages delivering other functionality (data handling, data acquisition,
  reporting, etc.)

---

### What's in the pipeline

##### `irispie`

* Estimation (including Bayes) of *structural* models, priors, system priors

* Nonlinear quasi-filtering

* Factor models

##### `cellport`

* Excel-based reporting

---

### What's different

* Python itself is different (see the last two sections)

* Our own more structured approach to designing packages (a larger number of
  smaller packages, with a clear focus)

* Modeling logic essentially the same, however with more of "explicit better
  than implicit", "only one way to do a thing"

* A side-by-side comparison of the Iris Toolbox and `irispie` is provided
  separately


---

### Python as an environment (versus Matlab)

* No single/universal out-of-the-box environment (editor, IDE, workspace, ...)

* In fact, plethora of them... each with some strong and some weak points

* Packages are installed with `pip`, ideally into a separate virtual
  environment for each project


---

### Python as a language (versus Matlab)

* A true general purpose language

* Flexible, easy to write and read, very good data structures

* Extremely extensive ecosystem of packages

* A couple of gotchas:

  * no scripts in the Matlab sense (each file has its own namespace)

  * assignment by reference (copy explicitly when you need a copy)

  * methods rather than functions (`model.simulate(...)`)

  * plain lists are indexed from 0 (time series are indexed by period)

  * indentation is part of the syntax


---

### Where to go next

* The workshop `README.md`: the model, the scripts, and how to run them

* The side-by-side Iris Toolbox vs `irispie` comparison

* `irispie` tutorials and documentation:
  https://iris-solutions-team.github.io/irispie-pages
