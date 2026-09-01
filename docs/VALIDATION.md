# Validation record

## Frozen-point numerical identity

The public Python mission evaluator was validated hierarchically against the
frozen reference implementation before release.

| Stage | Result |
|---|---|
| Atmosphere + source-anchored trajectory | PASS |
| Propulsion interface / PCHIP | PASS |
| Mass primitives | PASS |
| Segment mass ratio + 10-iteration closure | PASS |
| Air-breathing node and segment construction | PASS |
| Full Case-21 mission evaluator | PASS |
| 45-case frozen-point regression | 45/45 PASS |
| Objective + constraints wrapper | PASS |

Key final frozen-regression result:

- 45/45 cases passed;
- maximum absolute TOGW error: approximately `2.44e-12 t`;
- hard regression tolerance: `1e-8 t`.

Representative Case 21 full-evaluator error was approximately
`3.98e-13 t`.

## Independent optimization

The Python optimizer is deliberately independent of the frozen reference global-search optimizer search path.

Representative Case 21:

- frozen TOGW: `415.884533711041 t`;
- independent Python optimized TOGW: approximately `415.884490976727 t`;
- difference: approximately `-4.27e-05 t`;
- the optimized `Mcat`, ramjet-start condition, and separation parameter
  recovered the same engineering optimum basin.

All-45-case independent optimization:

- valid/physical: 45/45;
- engineering TOGW comparison: 45/45;
- coordinate-basin diagnostic: 45/45;
- maximum absolute optimized-TOGW difference: approximately `3.32e-04 t`;
- no stronger retry was required in the completed batch;
- independently optimized `Mcat` values remained tightly clustered near
  `1.153576827`, supporting the same manuscript-level optimum-location
  conclusion.

## Interpretation

Frozen-point regression is the hard numerical-identity gate.

Independent optimization is a reproducibility demonstration showing that a
different global optimization algorithm recovers the same engineering optimum
basin. It is not expected to reproduce the stochastic frozen reference global-search optimizer path or the
last decimal places of the optimizer coordinates.
