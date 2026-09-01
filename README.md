# CLRS-TSTO Python Reproducibility Package v1.0

Compact reviewer-facing Python implementation of the electromagnetic-launch
and mission-level mixed-propulsion TSTO mass-optimization model used for the
vehicle-level results in the study.

The Python implementation was numerically verified against the final frozen
45-case reference dataset before release. It is provided as a compact
reproducibility package rather than as the complete internal
research-development archive.

## Scope

This package includes the mission-level calculation chain required to inspect
and reproduce the principal vehicle-level results:

- ground-based electromagnetic release at `Hcat = 0 km`;
- first-order constant-acceleration launcher length, time, energy, and power;
- standard-atmosphere calculation;
- source-anchored Mach-altitude trajectory;
- ramjet / DMR-transition / scramjet propulsion-performance interface;
- gravity-loss calculation;
- first-stage structural-mass correction associated with release dynamic
  pressure;
- segmented first-stage mass-ratio calculation;
- two-stage mass closure;
- complete mission evaluator;
- representative Case-21 frozen-point regression;
- all-45-case frozen-point regression;
- representative Case-21 independent optimization.

The following parts of the broader study are **not included as executable
solvers** in this compact reviewer package:

- regenerative-cooling calculations;
- thermal-management solver;
- supercritical-CO2 closed-Brayton-cycle (`sCO2-CBC`) solver;
- REFPROP-based real-fluid property calculations;
- chronological battery / mission-energy recoupling.

Accordingly, executable reproducibility in this package is focused on the
mission-level electromagnetic-launch and vehicle-mass optimization results. It
does **not** claim to regenerate the complete thermal-electrical calculation
chain or every figure and result in the manuscript.

For reviewer inspection, a compact machine-readable summary of selected
thermal-electrical numerical values explicitly reported in the manuscript is
provided under `data/thermal_electrical_summary/`. These summary values are
documentary materials rather than raw case-wise datasets and do not constitute
an executable thermal-electrical solver.

## Tested environment

The release was validated with:

- Python 3.11;
- NumPy 2.4.6;
- pandas 3.0.5;
- SciPy 1.17.1;
- pytest 9.1.1.

Install the tested dependencies from the repository root:

```bash
pip install -r requirements.txt
```

## Quick start

From the repository root, run:

```bash
python check_package.py
python check_anonymity.py
python -m pytest
python run_all.py
```

Expected final messages include:

```text
PYTHON PUBLIC PACKAGE CHECK: PASS
RF-2 DOUBLE-ANONYMOUS PACKAGE CHECK: PASS
FINAL PYTHON ELECTROMAGNETIC-LAUNCH AUDIT: PASS
FINAL PYTHON SOURCE-ANCHORED TRAJECTORY AUDIT: PASS
FINAL PYTHON EXACT CASE-21 REGRESSION: PASS
FINAL PYTHON EXACT 45-CASE REGRESSION: PASS
ALL CORE PYTHON REPRODUCIBILITY CHECKS PASSED
```

To perform an independent optimization of the representative Case 21:

```bash
python optimize_baseline_case.py
```

This optimization intentionally uses a global-search procedure that is
independent of the frozen reference solution. It is used to test recovery of
the same engineering optimum basin rather than to reproduce a stochastic
search path point-for-point.

## Representative reference case

Case 21:

- architecture: `DMR`;
- `M_Ram,min = 2.5`;
- performance scenario: `REFERENCE`;
- `M_tr,end = 6.5`;
- `TOGW = 415.884533711041 t`;
- `M_cat,opt = 1.15357661420967`;
- `M_Ram,start,opt = 2.5`;
- `H_Ram,start = 15 km`;
- `lambda_sep = 0.123042403208665`.

## Numerical validation

Frozen-point regression is the hard numerical-identity check.

In the tested environment:

- all 45 frozen formal cases passed;
- the maximum absolute TOGW difference was approximately `2.44e-12 t`;
- the hard frozen-point tolerance is `1e-8 t`.

A separate independent-optimization assessment also recovered valid physical
solutions in the same engineering optimum basin. Because stochastic global
optimizers need not follow the same search path, optimizer-coordinate
agreement is treated as supporting reproducibility evidence rather than as the
hard numerical-identity criterion.

The runnable independent-optimization example in this compact package is
Case 21. The `validation/` directory also contains the archived results of the
completed 45-case independent-optimization assessment for documentation.

See `docs/VALIDATION.md` for the validation hierarchy and numerical results.

## Repository structure

```text
.
├── README.md
├── LICENSE
├── requirements.txt
├── pyproject.toml
├── check_package.py
├── check_anonymity.py
├── run_all.py
├── run_launcher_check.py
├── run_trajectory_check.py
├── run_baseline_case.py
├── run_45case_regression.py
├── optimize_baseline_case.py
├── clrs_tsto/
│   ├── __init__.py
│   ├── atmosphere.py
│   ├── cases.py
│   ├── config.py
│   ├── constants.py
│   ├── launcher.py
│   ├── mass_model.py
│   ├── mission.py
│   ├── mission_nodes.py
│   ├── optimization.py
│   ├── optimizer.py
│   ├── propulsion.py
│   ├── regression.py
│   ├── structure.py
│   └── trajectory.py
├── data/
│   ├── propulsion/
│   ├── reference/
│   └── thermal_electrical_summary/
├── validation/
├── tests/
└── docs/
```

## Data and verification basis

The propulsion-performance CSV values are distributed without refitting in
this Python release. The final frozen 45-case reference dataset used for
numerical regression is distributed under:

```text
data/reference/Step3R2D_formal_master_45case.csv
```

The Python implementation was numerically verified against this frozen
reference dataset before release. The repository also includes a compact
machine-readable summary of selected thermal-electrical values explicitly
reported in the manuscript under `data/thermal_electrical_summary/`. This
summary is provided for reviewer inspection and is not part of the executable
numerical-regression chain.

## Third-party software

REFPROP and other proprietary third-party software are not required to run the
mission-level Python package distributed here and are not redistributed.

## Double-anonymous review note

Author-identifying citation metadata is intentionally omitted from this
reviewer-facing package during double-anonymous review. A formal
`CITATION.cff` should be added only when disclosure of author identity is
permitted.

The reviewer-facing source files are prepared without author names,
affiliations, email addresses, ORCID identifiers, personal repository/profile
URLs, or local machine paths. The repository history starts with this
reviewer-facing release. Repository hosting can still reveal identity; during
double-anonymous review, this package should therefore be distributed only
through a journal-approved anonymous mechanism or another route consistent
with the journal's review policy.

## License

This software is released under the MIT License. See `LICENSE`.
