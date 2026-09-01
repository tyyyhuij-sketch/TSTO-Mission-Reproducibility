from pathlib import Path

from clrs_tsto.launcher import (
    MANKINS_REFERENCE_LENGTH_M,
    equivalent_acceleration_g0,
    launcher_requirements,
)
from clrs_tsto.mission import evaluate_design


def _load_case21(project_root):
    import pandas as pd
    from clrs_tsto.cases import build_case

    reference_file = (
        project_root
        / "data"
        / "reference"
        / "Step3R2D_formal_master_45case.csv"
    )

    table = pd.read_csv(reference_file)
    row = table[table["CaseID"] == 21]

    if len(row) != 1:
        raise AssertionError("Case 21 missing or duplicated.")

    r = row.iloc[0]

    case = build_case(
        architecture=str(r["Architecture"]),
        ram_min=float(r["MaRamMin"]),
        scenario=str(r["PerformanceScenario"]),
        transition_end_mach=float(r["TransitionEndMach"]),
        rocket2_mach=float(r["Rocket2Mach"]),
    )

    x = [
        float(r["MaTakeoffOpt"]),
        float(r["MaRamStartOpt"]),
        float(r["AlphaOpt"]),
    ]

    return r, case, x


def main():
    root = Path(__file__).resolve().parent

    r, case, x = _load_case21(root)
    d = evaluate_design(x, case)

    assert d.valid and d.physical_pass

    lr = launcher_requirements(
        vehicle_mass_t=d.tog_w_t,
        release_mach=float(r["MaTakeoffOpt"]),
        acceleration_g0=2.0,
        efficiency=0.80,
        altitude_km=0.0,
    )

    g_eq = equivalent_acceleration_g0(
        release_mach=float(r["MaTakeoffOpt"]),
        launcher_length_m=MANKINS_REFERENCE_LENGTH_M,
        altitude_km=0.0,
    )

    print()
    print("=== FINAL PYTHON ELECTROMAGNETIC-LAUNCH AUDIT ===")
    print(f"Case-21 TOGW                 = {d.tog_w_t:.12f} t")
    print(f"Release Mach                 = {lr.release_mach:.12f}")
    print(f"Release speed                = {lr.release_speed_mps:.6f} m/s")
    print(
        "Release dynamic pressure     = "
        f"{lr.release_dynamic_pressure_pa / 1000.0:.6f} kPa"
    )
    print(f"2g acceleration time         = {lr.acceleration_time_s:.6f} s")
    print(f"2g launch length             = {lr.launch_length_m / 1000.0:.6f} km")
    print(f"Input energy (eta=0.80)      = {lr.input_energy_j / 1e9:.6f} GJ")
    print(
        "Average input power          = "
        f"{lr.average_input_power_w / 1e9:.6f} GW"
    )
    print(
        "Terminal input power         = "
        f"{lr.terminal_input_power_w / 1e9:.6f} GW"
    )
    print(f"2.5-mile equivalent accel.   = {g_eq:.6f} g0")

    assert abs(d.tog_w_t - 415.884533711041) < 1e-8
    assert abs(d.h_ram_start_km - 15.0) < 1e-10
    assert abs(lr.launch_length_m / 1000.0 - 3.93) < 0.03
    assert abs(g_eq - 1.95) < 0.05

    print("FINAL PYTHON ELECTROMAGNETIC-LAUNCH AUDIT: PASS")


if __name__ == "__main__":
    main()
