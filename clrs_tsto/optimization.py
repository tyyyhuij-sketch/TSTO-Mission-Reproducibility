from dataclasses import dataclass

import numpy as np

from clrs_tsto.constants import PENALTY
from clrs_tsto.mission import evaluate_design


@dataclass(frozen=True)
class DesignBounds:
    """
    Frozen design-variable bounds used by reference implementation Step3R2D_optimize_case.

    Variable order:
        x[0] = MaTakeoff
        x[1] = MaRamStart
        x[2] = alpha
    """

    lower: np.ndarray
    upper: np.ndarray


def design_bounds(case):
    """
    Return the exact reference implementation lower/upper bounds for one case.

    reference implementation:
        Lb=[0; c.RamMin; 0];
        Ub=[3.0; 3.0; 0.2];
    """

    lower = np.asarray(
        [
            0.0,
            float(case.ram_min),
            0.0,
        ],
        dtype=np.float64,
    )

    upper = np.asarray(
        [
            3.0,
            3.0,
            0.2,
        ],
        dtype=np.float64,
    )

    return DesignBounds(
        lower=lower,
        upper=upper,
    )


def nonlinear_constraint_value(x):
    """
    Exact reference implementation Step3R2D_nonlcon inequality value.

    reference constraint convention:
        cineq <= 0 is feasible

    Here:
        cineq = MaTakeoff - MaRamStart
    """

    x = np.asarray(
        x,
        dtype=np.float64,
    ).reshape(-1)

    if x.size != 3:
        raise ValueError(
            "Design vector must contain exactly 3 variables."
        )

    return float(
        x[0] - x[1]
    )


def is_nonlinear_feasible(x, tolerance=0.0):
    """
    Check the reference implementation inequality convention cineq <= tolerance.
    """

    return bool(
        nonlinear_constraint_value(x)
        <= float(tolerance)
    )


def is_within_bounds(x, case):
    """
    Check the explicit global/local optimizer box bounds.

    This helper mirrors the bounds supplied by Step3R2D_optimize_case.
    It does not replace evaluate_design()'s internal physical checks.
    """

    x = np.asarray(
        x,
        dtype=np.float64,
    ).reshape(-1)

    if x.size != 3:
        return False

    if not np.all(np.isfinite(x)):
        return False

    bounds = design_bounds(case)

    return bool(
        np.all(x >= bounds.lower)
        and np.all(x <= bounds.upper)
    )


def objective(x, case):
    """
    Scientific-equivalent port of reference implementation Step3R2D_objective.

    reference implementation behavior:
        if design.Valid && design.PhysicalPass &&
           isfinite(design.TOGW_t) && design.TOGW_t > 0
            f = design.TOGW_t
        else
            f = cfg.Penalty
        end
    """

    design = evaluate_design(
        x,
        case,
    )

    tog_w = float(
        design.tog_w_t
    )

    if (
        design.valid
        and design.physical_pass
        and np.isfinite(tog_w)
        and tog_w > 0.0
    ):
        return tog_w

    return float(PENALTY)


def scipy_inequality_margin(x):
    """
    Convenience adapter for SciPy optimizers using g(x) >= 0.

    This is NOT a different constraint. It is simply the sign-reversed
    form of the reference implementation cineq <= 0 convention:

        MaRamStart - MaTakeoff >= 0
    """

    return float(
        -nonlinear_constraint_value(x)
    )
