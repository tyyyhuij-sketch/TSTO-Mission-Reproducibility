from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from clrs_tsto.cases import build_case
from clrs_tsto.mission import evaluate_design


DEFAULT_TOGW_TOL_T = 1e-8


@dataclass(frozen=True)
class RegressionSummary:
    total_cases: int
    passed_cases: int
    failed_cases: int
    max_abs_togw_error_t: float
    worst_case_id: int
    mcat_min: float
    mcat_max: float
    tog_w_min_t: float
    tog_w_max_t: float


def _required_columns():
    return [
        "CaseID",
        "Architecture",
        "MaRamMin",
        "PerformanceScenario",
        "TransitionEndMach",
        "Rocket2Mach",
        "MaTakeoffOpt",
        "MaRamStartOpt",
        "AlphaOpt",
        "TOGW_t",
    ]


def run_frozen_45case_regression(
    reference_file,
    output_file=None,
    tolerance_t=DEFAULT_TOGW_TOL_T,
):
    """
    Re-evaluate all 45 frozen formal design points with the Python mission
    evaluator.

    This is the Python scientific-equivalent of reference implementation
    run_45case_regression.

    Parameters
    ----------
    reference_file : str or pathlib.Path
        Path to Step3R2D_formal_master_45case.csv.

    output_file : str or pathlib.Path or None
        Optional CSV path for per-case Python regression results.

    tolerance_t : float
        Hard TOGW identity gate [t]. Frozen default: 1e-8 t.

    Returns
    -------
    result : pandas.DataFrame
        One row per frozen case.

    summary : RegressionSummary
        Aggregate regression metrics.
    """

    reference_file = Path(reference_file)

    if not reference_file.is_file():
        raise FileNotFoundError(
            f"Missing frozen 45-case reference table:\n{reference_file}"
        )

    table = pd.read_csv(reference_file)

    missing = [
        name
        for name in _required_columns()
        if name not in table.columns
    ]

    if missing:
        raise ValueError(
            "Missing required columns in 45-case reference table: "
            + ", ".join(missing)
        )

    if len(table) != 45:
        raise AssertionError(
            f"Expected 45 frozen formal cases, found {len(table)}."
        )

    rows = []

    for _, r in table.iterrows():

        architecture = str(r["Architecture"]).upper()
        scenario = str(r["PerformanceScenario"]).upper()

        transition_end = r["TransitionEndMach"]

        if architecture == "RAMJET_ONLY":
            transition_end = np.nan

        case = build_case(
            architecture=architecture,
            ram_min=float(r["MaRamMin"]),
            scenario=scenario,
            transition_end_mach=transition_end,
            rocket2_mach=float(r["Rocket2Mach"]),
        )

        x = [
            float(r["MaTakeoffOpt"]),
            float(r["MaRamStartOpt"]),
            float(r["AlphaOpt"]),
        ]

        d = evaluate_design(
            x,
            case,
        )

        frozen_togw = float(
            r["TOGW_t"]
        )

        python_togw = float(
            d.tog_w_t
        )

        error = (
            python_togw
            - frozen_togw
        )

        absolute_error = abs(
            error
        )

        physical_pass = bool(
            d.valid
            and d.physical_pass
        )

        tog_w_pass = bool(
            np.isfinite(absolute_error)
            and absolute_error < tolerance_t
        )

        case_pass = bool(
            physical_pass
            and tog_w_pass
        )

        rows.append({
            "CaseID": int(r["CaseID"]),
            "Architecture": architecture,
            "MaRamMin": float(r["MaRamMin"]),
            "PerformanceScenario": scenario,
            "TransitionEndMach": transition_end,
            "Rocket2Mach": float(r["Rocket2Mach"]),
            "MaTakeoffOpt": float(r["MaTakeoffOpt"]),
            "MaRamStartOpt": float(r["MaRamStartOpt"]),
            "AlphaOpt": float(r["AlphaOpt"]),
            "FrozenTOGW_t": frozen_togw,
            "PythonTOGW_t": python_togw,
            "TOGWError_t": error,
            "AbsTOGWError_t": absolute_error,
            "Valid": bool(d.valid),
            "PhysicalPass": bool(d.physical_pass),
            "CasePass": case_pass,
            "Message": str(d.message),
            "Python_HRamStart_km": float(d.h_ram_start_km),
            "Python_MuTot1": float(d.mu_tot1),
            "Python_MuTot2": float(d.mu_tot2),
            "Python_FirstStageMass_t": float(d.first_stage_mass_t),
            "Python_SecondStageMass_t": float(d.second_stage_mass_t),
        })

    result = pd.DataFrame(
        rows
    ).sort_values(
        "CaseID"
    ).reset_index(
        drop=True
    )

    if output_file is not None:
        output_file = Path(
            output_file
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        result.to_csv(
            output_file,
            index=False,
            float_format="%.17g",
        )

    passed_cases = int(
        result["CasePass"].sum()
    )

    total_cases = int(
        len(result)
    )

    failed_cases = (
        total_cases
        - passed_cases
    )

    max_error = float(
        result["AbsTOGWError_t"].max()
    )

    worst_index = result[
        "AbsTOGWError_t"
    ].idxmax()

    worst_case_id = int(
        result.loc[
            worst_index,
            "CaseID",
        ]
    )

    summary = RegressionSummary(
        total_cases=total_cases,
        passed_cases=passed_cases,
        failed_cases=failed_cases,
        max_abs_togw_error_t=max_error,
        worst_case_id=worst_case_id,
        mcat_min=float(
            table["MaTakeoffOpt"].min()
        ),
        mcat_max=float(
            table["MaTakeoffOpt"].max()
        ),
        tog_w_min_t=float(
            table["TOGW_t"].min()
        ),
        tog_w_max_t=float(
            table["TOGW_t"].max()
        ),
    )

    return result, summary
