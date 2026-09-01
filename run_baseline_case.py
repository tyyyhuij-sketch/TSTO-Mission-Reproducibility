from pathlib import Path

import pandas as pd

from clrs_tsto.cases import build_case
from clrs_tsto.mission import evaluate_design


def main():
    root = Path(__file__).resolve().parent

    reference_file = (
        root
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

    d = evaluate_design(x, case)

    error = d.tog_w_t - float(r["TOGW_t"])

    print()
    print("=== FINAL PYTHON EXACT CASE-21 REGRESSION ===")
    print(f"Frozen TOGW       = {float(r['TOGW_t']):.15f} t")
    print(f"Python TOGW       = {d.tog_w_t:.15f} t")
    print(f"Difference        = {error:+.17e} t")
    print(f"Mcat              = {d.ma_takeoff:.15f}")
    print(f"Mram,start        = {d.ma_ram_start:.15f}")
    print(f"Hram,start        = {d.h_ram_start_km:.15f} km")
    print(f"lambda_sep        = {d.alpha:.15f}")
    print(f"Valid/Physical    = {d.valid}/{d.physical_pass}")

    assert d.valid and d.physical_pass
    assert abs(error) < 1e-8
    assert abs(d.h_ram_start_km - 15.0) < 1e-10

    print("FINAL PYTHON EXACT CASE-21 REGRESSION: PASS")


if __name__ == "__main__":
    main()
