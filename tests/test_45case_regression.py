from pathlib import Path

from clrs_tsto.regression import run_frozen_45case_regression


def test_frozen_45case_regression():

    project_root = Path(__file__).resolve().parents[1]

    reference_file = (
        project_root
        / "data"
        / "reference"
        / "Step3R2D_formal_master_45case.csv"
    )

    result, summary = run_frozen_45case_regression(
        reference_file=reference_file,
        output_file=None,
        tolerance_t=1e-8,
    )

    print()
    print("=== pytest 45-case regression ===")
    print(
        "Cases passed =",
        summary.passed_cases,
        "/",
        summary.total_cases,
    )
    print(
        "Max |TOGW error| =",
        summary.max_abs_togw_error_t,
        "t",
    )

    assert len(result) == 45
    assert summary.passed_cases == 45
    assert summary.failed_cases == 0
    assert summary.max_abs_togw_error_t < 1e-8
