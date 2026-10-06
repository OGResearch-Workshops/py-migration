
# Migrating `.m` to `.py`

---

### Why away from Matlab

* Cost of Matlab

* Less familiarity with Matlab in new hires

* Inefficiency of closed-source commercial solution ("ecosystem")


---

### Why Python

* Scriptable non-compiled language

* Sensible numerical analysis, matrix algebra

* Business continuity

* Our choice was between Python vs Julia


---

### What's ready

* Our own package(s), source-available licensing

* Modeling package(s) replicating and extending the functionality of
  the Iris Toolbox

* Packages delivering other functionality (reporting, data acquisition, etc.)

---

### What's missing but in the pipeline

* Estimation, priors, system priors


---

### What's different

* Python's different (coming to that later)

* Our own more structured approach to designing packages (a larger number of
  smaller packages, with a clear focus)

* Modeling logic exactly the same, however with more of "explicit better than
  implicit", "only one way to do a thing"


---

### Python as an environment (versus Matlab)

* No single/universal out-of-the-box environment (editor, IDE, workspace, ...)

* In fact, plethora of them... each with some strong and some weak points

* Python packages


---

### Python as a language (versus Matlab)

* A true general purpose language

* Flexible, easy to write and read, very good data structures

* Extremely extensive ecosystem of packages

* A couple of gotchas: no scripts, assignment by reference, functions vs
  methods, 


