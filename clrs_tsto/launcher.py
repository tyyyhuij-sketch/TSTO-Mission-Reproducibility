from dataclasses import dataclass
import math

from clrs_tsto.atmosphere import atmosphere
from clrs_tsto.constants import GAMMA, RA_J_PER_KG_K


STANDARD_G0_MPS2 = 9.80665
DEFAULT_EM_EFFICIENCY = 0.80
MANKINS_REFERENCE_LENGTH_M = 2.5 * 1609.344


@dataclass(frozen=True)
class LauncherResult:
    release_mach: float
    release_speed_mps: float
    release_dynamic_pressure_pa: float
    acceleration_mps2: float
    acceleration_g0: float
    acceleration_time_s: float
    launch_length_m: float
    input_energy_j: float
    average_input_power_w: float
    terminal_input_power_w: float


def release_state(
    release_mach,
    altitude_km=0.0,
):
    """
    Frozen reviewer-facing electromagnetic-release state.

    The revised study uses a ground-based launcher at Hcat = 0 km.
    """

    release_mach = float(release_mach)
    altitude_km = float(altitude_km)

    if not math.isfinite(release_mach) or release_mach < 0.0:
        raise ValueError("release_mach must be finite and nonnegative.")

    pressure_pa, temperature_k = atmosphere(
        altitude_km
    )

    speed_mps = (
        release_mach
        * math.sqrt(
            GAMMA
            * RA_J_PER_KG_K
            * temperature_k
        )
    )

    dynamic_pressure_pa = (
        GAMMA
        * pressure_pa
        * release_mach**2
        / 2.0
    )

    return (
        float(speed_mps),
        float(dynamic_pressure_pa),
    )


def launcher_requirements(
    vehicle_mass_t,
    release_mach,
    acceleration_g0=2.0,
    efficiency=DEFAULT_EM_EFFICIENCY,
    altitude_km=0.0,
):
    """
    First-order constant-acceleration electromagnetic-launch requirements.

    Scientific-equivalent port of the equations used by run_launcher_check:
        L = u^2 / (2 a)
        t = u / a
        Ein = m u^2 / (2 eta)
        Pavg = Ein / t
        Pterminal = 2 Pavg

    Vehicle mass is supplied in tonnes and converted to kg for energy.
    """

    vehicle_mass_t = float(vehicle_mass_t)
    acceleration_g0 = float(acceleration_g0)
    efficiency = float(efficiency)

    if not math.isfinite(vehicle_mass_t) or vehicle_mass_t <= 0.0:
        raise ValueError("vehicle_mass_t must be finite and positive.")

    if not math.isfinite(acceleration_g0) or acceleration_g0 <= 0.0:
        raise ValueError("acceleration_g0 must be finite and positive.")

    if (
        not math.isfinite(efficiency)
        or efficiency <= 0.0
        or efficiency > 1.0
    ):
        raise ValueError("efficiency must satisfy 0 < efficiency <= 1.")

    release_speed_mps, q_release_pa = release_state(
        release_mach,
        altitude_km=altitude_km,
    )

    acceleration_mps2 = (
        acceleration_g0
        * STANDARD_G0_MPS2
    )

    launch_length_m = (
        release_speed_mps**2
        / (2.0 * acceleration_mps2)
    )

    acceleration_time_s = (
        release_speed_mps
        / acceleration_mps2
    )

    mass_kg = (
        vehicle_mass_t
        * 1000.0
    )

    input_energy_j = (
        mass_kg
        * release_speed_mps**2
        / (2.0 * efficiency)
    )

    average_input_power_w = (
        input_energy_j
        / acceleration_time_s
    )

    terminal_input_power_w = (
        2.0
        * average_input_power_w
    )

    return LauncherResult(
        release_mach=float(release_mach),
        release_speed_mps=float(release_speed_mps),
        release_dynamic_pressure_pa=float(q_release_pa),
        acceleration_mps2=float(acceleration_mps2),
        acceleration_g0=float(acceleration_g0),
        acceleration_time_s=float(acceleration_time_s),
        launch_length_m=float(launch_length_m),
        input_energy_j=float(input_energy_j),
        average_input_power_w=float(average_input_power_w),
        terminal_input_power_w=float(terminal_input_power_w),
    )


def equivalent_acceleration_g0(
    release_mach,
    launcher_length_m=MANKINS_REFERENCE_LENGTH_M,
    altitude_km=0.0,
):
    """
    Equivalent constant longitudinal acceleration for a prescribed launcher
    length at the same release speed.
    """

    launcher_length_m = float(
        launcher_length_m
    )

    if (
        not math.isfinite(launcher_length_m)
        or launcher_length_m <= 0.0
    ):
        raise ValueError("launcher_length_m must be finite and positive.")

    release_speed_mps, _ = release_state(
        release_mach,
        altitude_km=altitude_km,
    )

    acceleration_mps2 = (
        release_speed_mps**2
        / (2.0 * launcher_length_m)
    )

    return float(
        acceleration_mps2
        / STANDARD_G0_MPS2
    )
