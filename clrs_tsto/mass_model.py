import math
from dataclasses import dataclass

from clrs_tsto.structure import frame_mass_coefficient


G = 9.81
DEFAULT_DEN_TOL = 1e-10
DEFAULT_CLOSURE_ITERATIONS = 10


def gravity_loss(
    h1_km,
    h2_km,
    v1_mps,
    v2_mps,
):
    """
    Scientific-equivalent port of reference implementation GravityLoss.
    """

    values = [h1_km, h2_km, v1_mps, v2_mps]

    if not all(math.isfinite(float(v)) for v in values):
        raise ValueError("All inputs must be finite.")

    if (v1_mps + v2_mps) <= 0.0:
        raise ValueError("V1+V2 must be positive.")

    h1_m = 1000.0 * h1_km
    h2_m = 1000.0 * h2_km

    delta_vg = (
        2.0
        * G
        * (h2_m - h1_m)
        /
        (v2_mps + v1_mps)
    )

    return float(delta_vg)


def segment_mass_ratio(
    delta_v_mps,
    gravity_loss_mps,
    isp_s,
    g=G,
):
    """
    Segment mass ratio from the frozen Step3R2D mission equation:

        Mu = exp((deltaV + deltaVg) / (g * Isp))
    """

    values = [
        delta_v_mps,
        gravity_loss_mps,
        isp_s,
        g,
    ]

    if not all(math.isfinite(float(v)) for v in values):
        raise ValueError("All segment mass-ratio inputs must be finite.")

    if isp_s <= 0.0:
        raise ValueError("Isp must be positive.")

    if g <= 0.0:
        raise ValueError("g must be positive.")

    delta_v_eff = delta_v_mps + gravity_loss_mps

    mu = math.exp(
        delta_v_eff
        /
        (g * isp_s)
    )

    return float(mu)


def multiply_mass_ratios(mass_ratios):
    """
    Multiply segment mass ratios in explicit left-to-right order.
    """

    mu_total = 1.0

    for value in mass_ratios:
        value = float(value)

        if not math.isfinite(value):
            raise ValueError("Mass ratios must be finite.")

        mu_total *= value

    return float(mu_total)


def second_stage_vehicle_mass(
    m_load,
    sigma2nd,
    mu_tot2nd,
):
    """
    Scientific-equivalent port of reference implementation SecondStageVehicleMass.
    """

    return float(
        m_load
        * (mu_tot2nd - 1.0)
        /
        (1.0 - sigma2nd * mu_tot2nd)
    )


def vehicle_total_mass(
    m_load,
    sigma1st,
    sigma2nd,
    mu_tot1st,
    mu_tot2nd,
):
    """
    Scientific-equivalent port of reference implementation VehicleTotalMass.
    """

    return float(
        m_load
        * mu_tot1st
        * mu_tot2nd
        * (1.0 - sigma1st)
        * (1.0 - sigma2nd)
        /
        (1.0 - sigma1st * mu_tot1st)
        /
        (1.0 - sigma2nd * mu_tot2nd)
    )


@dataclass(frozen=True)
class MassClosureResult:
    total_mass_t: float
    first_stage_mass_t: float
    second_stage_mass_t: float
    sigma1: float
    ratio_ld: float
    iterations: int


def two_stage_mass_closure(
    m_load,
    sigma1st_rbcc,
    sigma2nd,
    mu_tot1,
    mu_tot2,
    ma_takeoff,
    h_takeoff_km=0.0,
    den_tol=DEFAULT_DEN_TOL,
    iterations=DEFAULT_CLOSURE_ITERATIONS,
):
    """
    Exact 10-iteration mass-closure sequence used by
    Step3R2D_compute_design.

    The iteration count is intentionally fixed to 10, matching reference implementation.
    """

    values = [
        m_load,
        sigma1st_rbcc,
        sigma2nd,
        mu_tot1,
        mu_tot2,
        ma_takeoff,
        h_takeoff_km,
        den_tol,
    ]

    if not all(math.isfinite(float(v)) for v in values):
        raise ValueError("Mass-closure inputs must be finite.")

    if iterations != 10:
        raise ValueError(
            "Frozen Step3R2D mass closure requires exactly 10 iterations."
        )

    if mu_tot1 <= 1.0 or mu_tot2 <= 1.0:
        raise ValueError("Total mass ratios must both be greater than 1.")

    if 1.0 - sigma2nd * mu_tot2 <= den_tol:
        raise ValueError("Second-stage denominator infeasible.")

    m1 = 100.0

    mtot = math.nan
    m2 = math.nan
    sigma1 = math.nan
    ratio_ld = math.nan

    for _ in range(iterations):

        sigma1, ratio_ld = frame_mass_coefficient(
            m1,
            ma_takeoff,
            h_takeoff_km,
            sigma1st_rbcc,
        )

        if 1.0 - sigma1 * mu_tot1 <= den_tol:
            raise ValueError("First-stage denominator infeasible.")

        mtot = vehicle_total_mass(
            m_load,
            sigma1,
            sigma2nd,
            mu_tot1,
            mu_tot2,
        )

        m2 = second_stage_vehicle_mass(
            m_load,
            sigma2nd,
            mu_tot2,
        )

        m1_new = mtot - m2 - m_load

        if (
            not all(
                math.isfinite(v)
                for v in [mtot, m2, m1_new]
            )
            or mtot <= 0.0
            or m2 <= 0.0
            or m1_new <= 0.0
        ):
            raise ValueError("Invalid coupled mass solution.")

        m1 = m1_new

    return MassClosureResult(
        total_mass_t=float(mtot),
        first_stage_mass_t=float(m1),
        second_stage_mass_t=float(m2),
        sigma1=float(sigma1),
        ratio_ld=float(ratio_ld),
        iterations=int(iterations),
    )
