# Public-package scope

This repository intentionally contains only the final Python implementation
required for the reviewer-facing mission-level reproducibility chain.

Included:
- electromagnetic launch/release engineering-scale calculation;
- atmosphere and source-anchored trajectory;
- propulsion uncertainty-interface data and interpolation;
- structural correction and gravity loss;
- segmented first-stage mass ratios;
- second-stage insertion and two-stage mass closure;
- complete mission evaluator;
- frozen 45-case regression;
- representative independent optimization.

Excluded:
- old/legacy/hotfix/debug source;
- reference implementation source files;
- internal checkpoints;
- personal absolute paths;
- obsolete ~437.1-t baseline;
- old fixed 18-km ramjet-start model;
- old 337-s rocket baseline;
- old 98.5-kPa high-Mach trajectory;
- regenerative cooling;
- thermal-management solver;
- sCO2-CBC;
- REFPROP;
- battery/mission-energy recoupling.

The exclusion of the thermal/electrical chain is deliberate and should be
stated explicitly whenever the repository scope is described.
