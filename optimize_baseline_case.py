from pathlib import Path

import pandas as pd

from clrs_tsto.cases import build_case
from clrs_tsto.mission import evaluate_design
from clrs_tsto.optimizer import optimize_case_independent


# PY-7B basin/reproducibility tolerances.
#
# These are deliberately looser than the 1e-8 t frozen-point identity gate.
# A stochastic optimizer is not expected to reproduce the frozen reference optimizer coordinates
# to the final decimal places.
TOGW_BASIN_TOL_T = 1e-3
MCAT_BASIN_TOL = 2e-3
MRAM_BASIN_TOL = 2e-3
ALPHA_BASIN_TOL = 2e-4


def main():
    project_root = Path(__file__).resolve().parent

    reference_file = (
        project_root
        / "data"
        / "reference"
        / "Step3R2D_formal_master_45case.csv"
    )

    if not reference_file.is_file():
        raise FileNotFoundError(
            f"Missing frozen 45-case reference table:\n{reference_file}"
        )

    table = pd.read_csv(
        reference_file
    )

    r = table[
        table["CaseID"] == 21
    ]

    if len(r) != 1:
        raise AssertionError(
            "Case 21 missing or duplicated."
        )

    r = r.iloc[0]

    case = build_case(
        architecture=str(
            r["Architecture"]
        ),
        ram_min=float(
            r["MaRamMin"]
        ),
        scenario=str(
            r["PerformanceScenario"]
        ),
        transition_end_mach=float(
            r["TransitionEndMach"]
        ),
        rocket2_mach=float(
            r["Rocket2Mach"]
        ),
    )

    frozen_x = [
        float(r["MaTakeoffOpt"]),
        float(r["MaRamStartOpt"]),
        float(r["AlphaOpt"]),
    ]

    frozen_togw = float(
        r["TOGW_t"]
    )

    seed = (
        int(r["Seed"])
        if "Seed" in table.columns
        else 2026082421
    )

    print()
    print("=== PY-7B CASE-21 INDEPENDENT OPTIMIZATION ===")
    print("Global optimizer = SciPy differential_evolution")
    print("Local polish     = SciPy SLSQP")
    print(f"Seed             = {seed}")
    print("This can take noticeably longer than the regression tests.")
    print()

    opt = optimize_case_independent(
        case=case,
        seed=seed,
        maxiter=260,
        popsize=15,
        tol=1e-9,
        atol=1e-9,
        local_polish=True,
    )

    design = evaluate_design(
        opt.x_final,
        case,
    )

    mcat = float(
        design.ma_takeoff
    )

    mram = float(
        design.ma_ram_start
    )

    alpha = float(
        design.alpha
    )

    tog_w = float(
        design.tog_w_t
    )

    d_togw = (
        tog_w
        - frozen_togw
    )

    d_mcat = (
        mcat
        - frozen_x[0]
    )

    d_mram = (
        mram
        - frozen_x[1]
    )

    d_alpha = (
        alpha
        - frozen_x[2]
    )

    print("Global-stage result:")
    print(
        f"  TOGW        = {opt.f_global:.15f} t"
    )
    print(
        f"  Mcat        = {opt.x_global[0]:.15f}"
    )
    print(
        f"  Mram,start  = {opt.x_global[1]:.15f}"
    )
    print(
        f"  lambda_sep  = {opt.x_global[2]:.15f}"
    )
    print(
        f"  success     = {opt.global_success}"
    )
    print(
        f"  iterations  = {opt.global_nit}"
    )
    print(
        f"  evaluations = {opt.global_nfev}"
    )
    print(
        f"  message     = {opt.global_message}"
    )

    print()
    print("Final result after optional SLSQP polish:")
    print(
        f"  TOGW        = {tog_w:.15f} t"
    )
    print(
        f"  Mcat        = {mcat:.15f}"
    )
    print(
        f"  Mram,start  = {mram:.15f}"
    )
    print(
        f"  Hram,start  = {design.h_ram_start_km:.15f} km"
    )
    print(
        f"  lambda_sep  = {alpha:.15f}"
    )
    print(
        f"  Local used  = {opt.local_used}"
    )
    print(
        f"  Local success= {opt.local_success}"
    )
    print(
        f"  Local message= {opt.local_message}"
    )
    print(
        f"  Valid/Physical = "
        f"{design.valid}/{design.physical_pass}"
    )

    print()
    print("Frozen Case-21 reference:")
    print(
        f"  TOGW        = {frozen_togw:.15f} t"
    )
    print(
        f"  Mcat        = {frozen_x[0]:.15f}"
    )
    print(
        f"  Mram,start  = {frozen_x[1]:.15f}"
    )
    print(
        f"  lambda_sep  = {frozen_x[2]:.15f}"
    )

    print()
    print("Independent-optimization differences:")
    print(
        f"  Delta TOGW       = {d_togw:+.17e} t"
    )
    print(
        f"  Delta Mcat       = {d_mcat:+.17e}"
    )
    print(
        f"  Delta Mram,start = {d_mram:+.17e}"
    )
    print(
        f"  Delta lambda_sep = {d_alpha:+.17e}"
    )

    output = pd.DataFrame(
        [
            {
                "CaseID": 21,
                "Seed": seed,
                "GlobalTOGW_t": opt.f_global,
                "GlobalMaTakeoff": opt.x_global[0],
                "GlobalMaRamStart": opt.x_global[1],
                "GlobalAlpha": opt.x_global[2],
                "GlobalSuccess": opt.global_success,
                "GlobalIterations": opt.global_nit,
                "GlobalEvaluations": opt.global_nfev,
                "LocalUsed": opt.local_used,
                "LocalSuccess": opt.local_success,
                "PythonOptimizedTOGW_t": tog_w,
                "PythonMaTakeoff": mcat,
                "PythonMaRamStart": mram,
                "PythonAlpha": alpha,
                "PythonHRamStart_km": design.h_ram_start_km,
                "FrozenTOGW_t": frozen_togw,
                "FrozenMaTakeoff": frozen_x[0],
                "FrozenMaRamStart": frozen_x[1],
                "FrozenAlpha": frozen_x[2],
                "DeltaTOGW_t": d_togw,
                "DeltaMaTakeoff": d_mcat,
                "DeltaMaRamStart": d_mram,
                "DeltaAlpha": d_alpha,
                "Valid": design.valid,
                "PhysicalPass": design.physical_pass,
            }
        ]
    )

    output_file = (
        project_root
        / "validation"
        / "python_case21_independent_optimization.csv"
    )

    output.to_csv(
        output_file,
        index=False,
        float_format="%.17g",
    )

    print()
    print(
        f"Output file = {output_file}"
    )

    same_basin = (
        design.valid
        and design.physical_pass
        and abs(d_togw) < TOGW_BASIN_TOL_T
        and abs(d_mcat) < MCAT_BASIN_TOL
        and abs(d_mram) < MRAM_BASIN_TOL
        and abs(d_alpha) < ALPHA_BASIN_TOL
        and abs(
            design.h_ram_start_km
            - 15.0
        ) < 5e-3
    )

    if not same_basin:
        raise AssertionError(
            "PY-7B independent optimizer did not recover the "
            "frozen Case-21 optimum basin."
        )

    print()
    print("PY-7B CASE-21 INDEPENDENT OPTIMIZATION: PASS")


if __name__ == "__main__":
    main()
