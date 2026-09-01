import numpy as np

from clrs_tsto.cases import build_case
from clrs_tsto.constants import PENALTY
from clrs_tsto.optimization import (
    design_bounds,
    is_nonlinear_feasible,
    is_within_bounds,
    nonlinear_constraint_value,
    objective,
    scipy_inequality_margin,
)


def _case21():
    return build_case(
        architecture="DMR",
        ram_min=2.5,
        scenario="REFERENCE",
        transition_end_mach=6.5,
        rocket2_mach=7.0,
    )


def test_case21_bounds():
    case = _case21()
    bounds = design_bounds(case)

    assert np.allclose(
        bounds.lower,
        [0.0, 2.5, 0.0],
        rtol=0.0,
        atol=0.0,
    )

    assert np.allclose(
        bounds.upper,
        [3.0, 3.0, 0.2],
        rtol=0.0,
        atol=0.0,
    )


def test_nonlinear_constraint_sign_convention():
    feasible = [1.0, 2.5, 0.1]
    violating = [2.6, 2.5, 0.1]

    assert nonlinear_constraint_value(feasible) == -1.5
    assert nonlinear_constraint_value(violating) > 0.0

    assert is_nonlinear_feasible(feasible)
    assert not is_nonlinear_feasible(violating)

    assert scipy_inequality_margin(feasible) == 1.5
    assert scipy_inequality_margin(violating) < 0.0


def test_case21_objective_at_frozen_point():
    case = _case21()

    x = [
        1.15357661420967,
        2.5,
        0.123042403208665,
    ]

    f = objective(
        x,
        case,
    )

    assert abs(
        f
        - 415.884533711041
    ) < 1e-8


def test_penalty_for_invalid_designs():
    case = _case21()

    invalid_points = [
        [-0.1, 2.5, 0.1],
        [1.0, 2.4, 0.1],
        [1.0, 2.5, 0.21],
        [2.6, 2.5, 0.1],
    ]

    for x in invalid_points:
        assert objective(x, case) == PENALTY


def test_explicit_bound_helper():
    case = _case21()

    assert is_within_bounds(
        [1.0, 2.5, 0.1],
        case,
    )

    assert not is_within_bounds(
        [-0.1, 2.5, 0.1],
        case,
    )

    assert not is_within_bounds(
        [1.0, 2.4, 0.1],
        case,
    )

    assert not is_within_bounds(
        [3.1, 3.0, 0.1],
        case,
    )
