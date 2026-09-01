from clrs_tsto.launcher import (
    MANKINS_REFERENCE_LENGTH_M,
    equivalent_acceleration_g0,
    launcher_requirements,
)


CASE21_TOGW_T = 415.884533711041
CASE21_MCAT = 1.15357661420967


def test_case21_launcher_audit():
    r = launcher_requirements(
        vehicle_mass_t=CASE21_TOGW_T,
        release_mach=CASE21_MCAT,
        acceleration_g0=2.0,
        efficiency=0.80,
        altitude_km=0.0,
    )

    g_eq = equivalent_acceleration_g0(
        release_mach=CASE21_MCAT,
        launcher_length_m=MANKINS_REFERENCE_LENGTH_M,
        altitude_km=0.0,
    )

    assert abs(
        r.launch_length_m / 1000.0
        - 3.93
    ) < 0.03

    assert abs(
        g_eq
        - 1.95
    ) < 0.05

    assert r.release_speed_mps > 0.0
    assert r.input_energy_j > 0.0
    assert r.average_input_power_w > 0.0
    assert r.terminal_input_power_w > 0.0
