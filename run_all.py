from check_package import main as check_package
from check_anonymity import main as check_anonymity
from run_launcher_check import main as run_launcher_check
from run_trajectory_check import main as run_trajectory_check
from run_baseline_case import main as run_baseline_case
from run_45case_regression import main as run_45case_regression


def main():
    print()
    print("============================================================")
    print("CLRS-TSTO PYTHON REPRODUCIBILITY PACKAGE v1.0")
    print("============================================================")

    check_package()
    check_anonymity()
    run_launcher_check()
    run_trajectory_check()
    run_baseline_case()
    run_45case_regression()

    print()
    print("============================================================")
    print("ALL CORE PYTHON REPRODUCIBILITY CHECKS PASSED")
    print(
        "For an independent representative optimization, "
        "run optimize_baseline_case.py separately."
    )
    print("============================================================")


if __name__ == "__main__":
    main()
