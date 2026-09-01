import math
from dataclasses import dataclass, field

import numpy as np

from clrs_tsto.atmosphere import atmosphere
from clrs_tsto.constants import (
    GAMMA,
    RA_J_PER_KG_K,
    G_MPS2,
    FIRST_STAGE_ROCKET_ISP_S,
    SECOND_STAGE_ROCKET_ISP_S,
    ORBIT_VELOCITY_MPS,
    ORBIT_ALTITUDE_KM,
    TAKEOFF_ALTITUDE_KM,
    PAYLOAD_MASS_T,
    SIGMA1ST_RBCC,
    SIGMA2ND,
    PENALTY,
    DEN_TOL,
    PHYSICAL_TOL,
)
from clrs_tsto.mass_model import (
    gravity_loss,
    multiply_mass_ratios,
    segment_mass_ratio,
    two_stage_mass_closure,
)
from clrs_tsto.mission_nodes import build_airbreathing_nodes
from clrs_tsto.propulsion import performance_at
from clrs_tsto.trajectory import reference_altitude


@dataclass
class MissionResult:
    valid: bool = False
    physical_pass: bool = False
    tog_w_t: float = PENALTY
    message: str = ""

    first_stage_mass_t: float = math.nan
    second_stage_mass_t: float = math.nan
    total_propellant_t: float = math.nan

    ma_takeoff: float = math.nan
    ma_ram_start: float = math.nan
    h_ram_start_km: float = math.nan
    alpha: float = math.nan

    architecture: str = ""
    performance_scenario: str = ""
    transition_end_mach: float = math.nan
    rocket2_mach: float = math.nan

    v_sep_mps: float = math.nan
    h_sep_km: float = math.nan
    delta_vg_1st_mps: float = math.nan
    delta_vg_2nd_mps: float = math.nan

    mu_tot1: float = math.nan
    mu_tot2: float = math.nan

    rocket1_propellant_t: float = math.nan
    ramjet_fuel_t: float = math.nan
    dmr_blend_fuel_t: float = math.nan
    scramjet_fuel_t: float = math.nan
    rocket2_first_stage_propellant_t: float = math.nan
    second_stage_propellant_t: float = math.nan

    min_delta_h_km: float = math.nan
    min_delta_v_eff_mps: float = math.nan
    min_segment_mu: float = math.nan
    min_segment_fuel_t: float = math.nan

    mach_nodes: np.ndarray = field(
        default_factory=lambda: np.asarray([], dtype=np.float64)
    )
    altitude_nodes_km: np.ndarray = field(
        default_factory=lambda: np.asarray([], dtype=np.float64)
    )
    segment_modes: tuple[str, ...] = field(default_factory=tuple)

    segment_types: tuple[str, ...] = field(default_factory=tuple)
    segment_isp_s: np.ndarray = field(
        default_factory=lambda: np.asarray([], dtype=np.float64)
    )
    segment_mass_ratio: np.ndarray = field(
        default_factory=lambda: np.asarray([], dtype=np.float64)
    )
    segment_fuel_t: np.ndarray = field(
        default_factory=lambda: np.asarray([], dtype=np.float64)
    )

    segment_mach_start: np.ndarray = field(
        default_factory=lambda: np.asarray([], dtype=np.float64)
    )
    segment_mach_end: np.ndarray = field(
        default_factory=lambda: np.asarray([], dtype=np.float64)
    )
    segment_mach_mid: np.ndarray = field(
        default_factory=lambda: np.asarray([], dtype=np.float64)
    )

    segment_altitude_start_km: np.ndarray = field(
        default_factory=lambda: np.asarray([], dtype=np.float64)
    )
    segment_altitude_end_km: np.ndarray = field(
        default_factory=lambda: np.asarray([], dtype=np.float64)
    )


def _sum_left_to_right(values):
    """
    Explicit scalar accumulation, avoiding a different vectorized reduction
    strategy when reference/Python regression is being audited.
    """

    total = 0.0

    for value in values:
        total += float(value)

    return float(total)


def _fuel_sum(segment_fuel, segment_types, requested_type):
    total = 0.0

    for fuel, seg_type in zip(segment_fuel, segment_types):
        if seg_type == requested_type:
            total += float(fuel)

    return float(total)


def evaluate_design(x, case):
    """
    Scientific-equivalent port of reference implementation Step3R2D_compute_design.

    Parameters
    ----------
    x : sequence of 3 floats
        [MaTakeoff, MaRamStart, alpha]

    case : MissionCase
        Frozen architecture/performance case.

    Returns
    -------
    MissionResult
    """

    out = MissionResult()

    try:
        x_array = np.asarray(x)

        if (
            x_array.size != 3
            or not np.isrealobj(x_array)
        ):
            out.message = "invalid design vector"
            return out

        x_values = [
            float(x_array.flat[0]),
            float(x_array.flat[1]),
            float(x_array.flat[2]),
        ]

        if not all(math.isfinite(v) for v in x_values):
            out.message = "invalid design vector"
            return out

        ma_takeoff, ma_ram_start, alpha = x_values

        if (
            ma_takeoff < 0.0
            or ma_ram_start < case.ram_min - 1e-10
            or ma_ram_start > 3.0 + 1e-10
            or alpha < 0.0
            or alpha > 0.2
            or ma_takeoff > ma_ram_start + 1e-12
        ):
            out.message = "design outside bounds"
            return out

        # ------------------------------------------------------------
        # Reference trajectory and velocity states
        # ------------------------------------------------------------
        h_ram_start = reference_altitude(ma_ram_start)

        _, t0 = atmosphere(TAKEOFF_ALTITUDE_KM)

        v_takeoff = (
            ma_takeoff
            * math.sqrt(
                GAMMA
                * RA_J_PER_KG_K
                * t0
            )
        )

        _, t_ram = atmosphere(h_ram_start)

        v_ram_start = (
            ma_ram_start
            * math.sqrt(
                GAMMA
                * RA_J_PER_KG_K
                * t_ram
            )
        )

        air = build_airbreathing_nodes(
            ma_ram_start,
            case,
        )

        v_ab = []

        for mach, altitude_km in zip(
            air.mach,
            air.altitude_km,
        ):
            _, temperature = atmosphere(
                float(altitude_km)
            )

            velocity = (
                float(mach)
                * math.sqrt(
                    GAMMA
                    * RA_J_PER_KG_K
                    * temperature
                )
            )

            v_ab.append(float(velocity))

        v_ab = np.asarray(
            v_ab,
            dtype=np.float64,
        )

        v_rkt2_start = float(v_ab[-1])
        h_rkt2_start = float(air.altitude_km[-1])

        v_sep = (
            v_rkt2_start
            + alpha
            * (
                ORBIT_VELOCITY_MPS
                - v_rkt2_start
            )
        )

        h_sep = (
            h_rkt2_start
            + alpha
            * (
                ORBIT_ALTITUDE_KM
                - h_rkt2_start
            )
        )

        # reference implementation:
        # Vnodes=[Vtakeoff VramStart Vab(2:end) Vsep];
        # Hnodes=[HtakeoffCARS HramStart Hab(2:end) Hsep];
        v_nodes = [
            float(v_takeoff),
            float(v_ram_start),
        ]

        v_nodes.extend(
            float(v)
            for v in v_ab[1:]
        )

        v_nodes.append(float(v_sep))

        h_nodes = [
            float(TAKEOFF_ALTITUDE_KM),
            float(h_ram_start),
        ]

        h_nodes.extend(
            float(h)
            for h in air.altitude_km[1:]
        )

        h_nodes.append(float(h_sep))

        n_seg = len(v_nodes) - 1

        segment_types = (
            ("ROCKET1",)
            + tuple(air.segment_modes)
            + ("ROCKET2",)
        )

        if len(segment_types) != n_seg:
            raise RuntimeError(
                "Internal segment construction mismatch."
            )

        # ------------------------------------------------------------
        # First-stage segment delta-V, gravity loss, Isp, mass ratio
        # ------------------------------------------------------------
        delta_v = []
        delta_vg = []
        isp = []

        air_index = 0

        for k in range(n_seg):

            dv = (
                float(v_nodes[k + 1])
                - float(v_nodes[k])
            )

            dvg = gravity_loss(
                float(h_nodes[k]),
                float(h_nodes[k + 1]),
                float(v_nodes[k]),
                float(v_nodes[k + 1]),
            )

            seg_type = segment_types[k]

            if seg_type in ("ROCKET1", "ROCKET2"):

                isp_value = FIRST_STAGE_ROCKET_ISP_S

            else:

                m_mid = 0.5 * (
                    float(air.mach[air_index])
                    + float(air.mach[air_index + 1])
                )

                isp_value = performance_at(
                    m_mid,
                    case,
                )

                air_index += 1

            delta_v.append(float(dv))
            delta_vg.append(float(dvg))
            isp.append(float(isp_value))

        if (
            not all(math.isfinite(v) for v in isp)
            or any(v <= 0.0 for v in isp)
        ):
            out.message = "invalid segment performance"
            return out

        delta_v_eff = [
            dv + dvg
            for dv, dvg in zip(
                delta_v,
                delta_vg,
            )
        ]

        mu = [
            segment_mass_ratio(
                dv,
                dvg,
                isp_value,
                g=G_MPS2,
            )
            for dv, dvg, isp_value in zip(
                delta_v,
                delta_vg,
                isp,
            )
        ]

        if (
            not all(math.isfinite(v) for v in mu)
            or any(v <= 0.0 for v in mu)
        ):
            out.message = "invalid first-stage mass ratios"
            return out

        mu_tot1 = multiply_mass_ratios(mu)

        # ------------------------------------------------------------
        # Second-stage mass ratio
        # ------------------------------------------------------------
        delta_v2 = (
            ORBIT_VELOCITY_MPS
            - v_sep
        )

        delta_vg2 = gravity_loss(
            h_sep,
            ORBIT_ALTITUDE_KM,
            v_sep,
            ORBIT_VELOCITY_MPS,
        )

        mu_tot2 = segment_mass_ratio(
            delta_v2,
            delta_vg2,
            SECOND_STAGE_ROCKET_ISP_S,
            g=G_MPS2,
        )

        if (
            not math.isfinite(mu_tot1)
            or not math.isfinite(mu_tot2)
            or mu_tot1 <= 1.0
            or mu_tot2 <= 1.0
        ):
            out.message = "invalid total mass ratio"
            return out

        if (
            1.0
            - SIGMA2ND * mu_tot2
            <= DEN_TOL
        ):
            out.message = "second-stage denominator infeasible"
            return out

        # ------------------------------------------------------------
        # Exact frozen 10-iteration coupled mass closure
        # ------------------------------------------------------------
        closure = two_stage_mass_closure(
            m_load=PAYLOAD_MASS_T,
            sigma1st_rbcc=SIGMA1ST_RBCC,
            sigma2nd=SIGMA2ND,
            mu_tot1=mu_tot1,
            mu_tot2=mu_tot2,
            ma_takeoff=ma_takeoff,
            h_takeoff_km=TAKEOFF_ALTITUDE_KM,
            den_tol=DEN_TOL,
            iterations=10,
        )

        mtot = closure.total_mass_t
        m1 = closure.first_stage_mass_t
        m2 = closure.second_stage_mass_t

        # ------------------------------------------------------------
        # Segment mass depletion and local physical gates
        # ------------------------------------------------------------
        mass = [float(mtot)]

        for mu_value in mu:
            mass.append(
                mass[-1]
                / float(mu_value)
            )

        dm = [
            mass[k] - mass[k + 1]
            for k in range(len(mu))
        ]

        delta_h = [
            float(h_nodes[k + 1])
            - float(h_nodes[k])
            for k in range(n_seg)
        ]

        physical_pass = (
            all(dh >= -PHYSICAL_TOL for dh in delta_h)
            and all(
                dve >= -PHYSICAL_TOL
                for dve in delta_v_eff
            )
            and all(
                mu_value >= 1.0 - PHYSICAL_TOL
                for mu_value in mu
            )
            and all(
                fuel >= -PHYSICAL_TOL
                for fuel in dm
            )
        )

        min_delta_h = min(delta_h)
        min_delta_v_eff = min(delta_v_eff)
        min_segment_mu = min(mu)
        min_segment_fuel = min(dm)

        if not physical_pass:
            out.message = "local physical gate failed"
            out.min_delta_h_km = float(min_delta_h)
            out.min_delta_v_eff_mps = float(min_delta_v_eff)
            out.min_segment_mu = float(min_segment_mu)
            out.min_segment_fuel_t = float(min_segment_fuel)
            return out

        # ------------------------------------------------------------
        # Propellant/fuel accounting
        # ------------------------------------------------------------
        ram_fuel = _fuel_sum(
            dm,
            segment_types,
            "RAMJET",
        )

        blend_fuel = _fuel_sum(
            dm,
            segment_types,
            "DMR_BLEND",
        )

        scr_fuel = _fuel_sum(
            dm,
            segment_types,
            "SCRAMJET",
        )

        rocket1_fuel = _fuel_sum(
            dm,
            segment_types,
            "ROCKET1",
        )

        rocket2_fuel = _fuel_sum(
            dm,
            segment_types,
            "ROCKET2",
        )

        second_stage_prop = (
            m2
            * (1.0 - SIGMA2ND)
        )

        # ------------------------------------------------------------
        # Segment Mach bookkeeping
        # ------------------------------------------------------------
        mach_start = np.full(
            n_seg,
            np.nan,
            dtype=np.float64,
        )

        mach_end = np.full(
            n_seg,
            np.nan,
            dtype=np.float64,
        )

        mach_mid = np.full(
            n_seg,
            np.nan,
            dtype=np.float64,
        )

        n_air = len(air.mach) - 1

        for j in range(n_air):

            # reference implementation j=1 -> kk=2.
            kk = j + 1

            mach_start[kk] = float(
                air.mach[j]
            )

            mach_end[kk] = float(
                air.mach[j + 1]
            )

            mach_mid[kk] = 0.5 * (
                float(air.mach[j])
                + float(air.mach[j + 1])
            )

        # ------------------------------------------------------------
        # Final output
        # ------------------------------------------------------------
        out.valid = True
        out.physical_pass = True
        out.message = "PASS"

        out.tog_w_t = float(mtot)
        out.first_stage_mass_t = float(m1)
        out.second_stage_mass_t = float(m2)

        out.total_propellant_t = (
            _sum_left_to_right(dm)
            + float(second_stage_prop)
        )

        out.ma_takeoff = float(ma_takeoff)
        out.ma_ram_start = float(ma_ram_start)
        out.h_ram_start_km = float(h_ram_start)
        out.alpha = float(alpha)

        out.architecture = case.architecture
        out.performance_scenario = case.scenario
        out.transition_end_mach = float(
            case.transition_end_mach
        )
        out.rocket2_mach = float(
            case.rocket2_mach
        )

        out.v_sep_mps = float(v_sep)
        out.h_sep_km = float(h_sep)

        out.delta_vg_1st_mps = _sum_left_to_right(
            delta_vg
        )

        out.delta_vg_2nd_mps = float(
            delta_vg2
        )

        out.mu_tot1 = float(mu_tot1)
        out.mu_tot2 = float(mu_tot2)

        out.rocket1_propellant_t = float(
            rocket1_fuel
        )
        out.ramjet_fuel_t = float(
            ram_fuel
        )
        out.dmr_blend_fuel_t = float(
            blend_fuel
        )
        out.scramjet_fuel_t = float(
            scr_fuel
        )
        out.rocket2_first_stage_propellant_t = float(
            rocket2_fuel
        )
        out.second_stage_propellant_t = float(
            second_stage_prop
        )

        out.min_delta_h_km = float(
            min_delta_h
        )
        out.min_delta_v_eff_mps = float(
            min_delta_v_eff
        )
        out.min_segment_mu = float(
            min_segment_mu
        )
        out.min_segment_fuel_t = float(
            min_segment_fuel
        )

        out.mach_nodes = np.asarray(
            air.mach,
            dtype=np.float64,
        )

        out.altitude_nodes_km = np.asarray(
            air.altitude_km,
            dtype=np.float64,
        )

        out.segment_modes = tuple(
            air.segment_modes
        )

        out.segment_types = tuple(
            segment_types
        )

        out.segment_isp_s = np.asarray(
            isp,
            dtype=np.float64,
        )

        out.segment_mass_ratio = np.asarray(
            mu,
            dtype=np.float64,
        )

        out.segment_fuel_t = np.asarray(
            dm,
            dtype=np.float64,
        )

        out.segment_mach_start = mach_start
        out.segment_mach_end = mach_end
        out.segment_mach_mid = mach_mid

        out.segment_altitude_start_km = np.asarray(
            h_nodes[:-1],
            dtype=np.float64,
        )

        out.segment_altitude_end_km = np.asarray(
            h_nodes[1:],
            dtype=np.float64,
        )

        return out

    except Exception as exc:
        out.valid = False
        out.physical_pass = False
        out.tog_w_t = PENALTY
        out.message = (
            f"{type(exc).__name__}: {exc}"
        )
        return out
