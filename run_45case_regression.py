from pathlib import Path

from clrs_tsto.regression import (
    DEFAULT_TOGW_TOL_T,
    run_frozen_45case_regression,
)


def main():
    root = Path(__file__).resolve().parent

    reference_file = (
        root
        / "data"
        / "reference"
        / "Step3R2D_formal_master_45case.csv"
    )

    output_file = (
        root
        / "validation"
        / "python_45case_regression.csv"
    )

    result, summary = run_frozen_45case_regression(
        reference_file=reference_file,
        output_file=output_file,
        tolerance_t=DEFAULT_TOGW_TOL_T,
    )

    worst = result.loc[
        result["AbsTOGWError_t"].idxmax()
    ]

    print()
    print("=== FINAL PYTHON EXACT 45-CASE REGRESSION ===")
    print(
        f"Cases passed       = "
        f"{summary.passed_cases}/{summary.total_cases}"
    )
    print(f"Cases failed       = {summary.failed_cases}")
    print(
        f"Max |TOGW error|   = "
        f"{summary.max_abs_togw_error_t:.17e} t"
    )
    print(f"Worst CaseID       = {summary.worst_case_id}")
    print(
        f"Frozen TOGW        = "
        f"{worst['FrozenTOGW_t']:.15f} t"
    )
    print(
        f"Python TOGW        = "
        f"{worst['PythonTOGW_t']:.15f} t"
    )
    print(
        f"Difference         = "
        f"{worst['TOGWError_t']:+.17e} t"
    )

    assert summary.passed_cases == 45
    assert summary.failed_cases == 0
    assert summary.max_abs_togw_error_t < DEFAULT_TOGW_TOL_T

    print("FINAL PYTHON EXACT 45-CASE REGRESSION: PASS")


if __name__ == "__main__":
    main()
