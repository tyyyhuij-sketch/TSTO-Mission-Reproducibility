from dataclasses import dataclass

import numpy as np
from scipy.optimize import (
    Bounds,
    LinearConstraint,
    differential_evolution,
    minimize,
)

from clrs_tsto.mission import evaluate_design
from clrs_tsto.optimization import (
    design_bounds,
    objective,
)


@dataclass(frozen=True)
class IndependentOptimizationResult:
    x_global: np.ndarray
    f_global: float
    global_success: bool
    global_message: str
    global_nfev: int
    global_nit: int

    x_final: np.ndarray
    f_final: float
    local_success: bool
    local_used: bool
    local_message: str
    local_nfev: int
    local_nit: int

    seed: int


def _scipy_bounds(case):
    b = design_bounds(case)

    return Bounds(
        lb=b.lower,
        ub=b.upper,
        keep_feasible=False,
    )


def _linear_constraint():
    """
    reference constraint:
        MaTakeoff - MaRamStart <= 0

    SciPy LinearConstraint form:
        -inf <= [1, -1, 0] @ x <= 0
    """

    return LinearConstraint(
        np.asarray(
            [[1.0, -1.0, 0.0]],
            dtype=np.float64,
        ),
        lb=np.asarray(
            [-np.inf],
            dtype=np.float64,
        ),
        ub=np.asarray(
            [0.0],
            dtype=np.float64,
        ),
    )


def _slsqp_constraint():
    """
    SLSQP dict convention:
        fun(x) >= 0 is feasible.

    Thus:
        MaRamStart - MaTakeoff >= 0.
    """

    return {
        "type": "ineq",
        "fun": lambda x: float(
            x[1] - x[0]
        ),
    }


def local_slsqp_polish(
    x0,
    case,
    *,
    maxiter=1000,
    ftol=1e-12,
):
    """
    Deterministic SLSQP local polish from a supplied feasible point.
    """

    b = design_bounds(case)

    result = minimize(
        fun=lambda x: objective(x, case),
        x0=np.asarray(
            x0,
            dtype=np.float64,
        ),
        method="SLSQP",
        bounds=list(
            zip(
                b.lower.tolist(),
                b.upper.tolist(),
            )
        ),
        constraints=(
            _slsqp_constraint(),
        ),
        options={
            "maxiter": int(maxiter),
            "ftol": float(ftol),
            "disp": False,
        },
    )

    return result


def optimize_case_independent(
    case,
    seed,
    *,
    maxiter=260,
    popsize=15,
    tol=1e-9,
    atol=1e-9,
    mutation=(0.5, 1.0),
    recombination=0.7,
    local_polish=True,
):
    """
    Independent Python global + local optimization.

    Global stage:
        scipy.optimize.differential_evolution

    Local stage:
        scipy.optimize.minimize(method="SLSQP")

    Notes
    -----
    This is intentionally NOT presented as a line-by-line reproduction of
    the frozen reference global-search implementation. The frozen reference implementation optimizer uses GA followed
    by optional SQP polish. Here the scientific objective, bounds, nonlinear
    inequality, and physical evaluator are identical, while the stochastic
    global-search algorithm is independently implemented in SciPy.
    """

    seed = int(seed)

    bounds = _scipy_bounds(case)
    constraint = _linear_constraint()

    global_result = differential_evolution(
        func=lambda x: objective(x, case),
        bounds=bounds,
        constraints=(constraint,),
        strategy="best1bin",
        maxiter=int(maxiter),
        popsize=int(popsize),
        tol=float(tol),
        atol=float(atol),
        mutation=mutation,
        recombination=float(recombination),
        rng=np.random.default_rng(seed),
        polish=False,
        updating="immediate",
        workers=1,
        disp=False,
    )

    x_global = np.asarray(
        global_result.x,
        dtype=np.float64,
    )

    f_global = float(
        global_result.fun
    )

    x_final = x_global.copy()
    f_final = f_global

    local_success = False
    local_used = False
    local_message = "local polish disabled"
    local_nfev = 0
    local_nit = 0

    if local_polish:

        local = local_slsqp_polish(
            x_global,
            case,
            maxiter=1000,
            ftol=1e-12,
        )

        local_success = bool(
            local.success
        )

        local_message = str(
            local.message
        )

        local_nfev = int(
            getattr(
                local,
                "nfev",
                0,
            )
        )

        local_nit = int(
            getattr(
                local,
                "nit",
                0,
            )
        )

        local_f = float(
            local.fun
        )

        if (
            local.success
            and np.isfinite(local_f)
            and local_f < f_final
        ):
            local_x = np.asarray(
                local.x,
                dtype=np.float64,
            )

            design = evaluate_design(
                local_x,
                case,
            )

            if (
                design.valid
                and design.physical_pass
            ):
                x_final = local_x
                f_final = local_f
                local_used = True

    final_design = evaluate_design(
        x_final,
        case,
    )

    if (
        not final_design.valid
        or not final_design.physical_pass
        or not np.isfinite(f_final)
    ):
        raise RuntimeError(
            "Independent optimizer did not return a feasible physical design: "
            f"{final_design.message}"
        )

    return IndependentOptimizationResult(
        x_global=x_global,
        f_global=f_global,
        global_success=bool(
            global_result.success
        ),
        global_message=str(
            global_result.message
        ),
        global_nfev=int(
            getattr(
                global_result,
                "nfev",
                0,
            )
        ),
        global_nit=int(
            getattr(
                global_result,
                "nit",
                0,
            )
        ),
        x_final=x_final,
        f_final=float(
            f_final
        ),
        local_success=local_success,
        local_used=local_used,
        local_message=local_message,
        local_nfev=local_nfev,
        local_nit=local_nit,
        seed=seed,
    )
