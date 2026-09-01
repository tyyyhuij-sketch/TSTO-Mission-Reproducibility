from pathlib import Path
import re


REQUIRED_FILES = [
    "README.md",
    "requirements.txt",
    "pyproject.toml",
    "LICENSE",
    "run_all.py",
    "check_anonymity.py",
    "run_launcher_check.py",
    "run_trajectory_check.py",
    "run_baseline_case.py",
    "run_45case_regression.py",
    "optimize_baseline_case.py",
    "clrs_tsto/__init__.py",
    "clrs_tsto/atmosphere.py",
    "clrs_tsto/cases.py",
    "clrs_tsto/config.py",
    "clrs_tsto/constants.py",
    "clrs_tsto/launcher.py",
    "clrs_tsto/mass_model.py",
    "clrs_tsto/mission.py",
    "clrs_tsto/mission_nodes.py",
    "clrs_tsto/optimization.py",
    "clrs_tsto/optimizer.py",
    "clrs_tsto/propulsion.py",
    "clrs_tsto/regression.py",
    "clrs_tsto/structure.py",
    "clrs_tsto/trajectory.py",
    "data/propulsion/V35B_0D_RAMJET_SCENARIOS.csv",
    "data/propulsion/V35B_0D_TRANSITION_BLEND_SCENARIOS.csv",
    "data/reference/Step3R2D_formal_master_45case.csv",
    "data/thermal_electrical_summary/README.md",
    "data/thermal_electrical_summary/reported_results_summary.csv",
]

FORBIDDEN_NAME_TOKENS = [
    "hotfix",
    "quick",
    "debug",
    "legacy",
    "checkpoint",
]

WINDOWS_ABS_PATH = re.compile(
    r"[A-Za-z]:\\(?:Users|PyCharm|Anaconda)\\",
    re.IGNORECASE,
)


def main():
    root = Path(__file__).resolve().parent

    print()
    print("=== PYTHON PUBLIC PACKAGE CHECK ===")

    for rel in REQUIRED_FILES:
        path = root / rel
        exists = path.is_file()
        print(f"{rel:<78} {exists}")
        assert exists, f"Missing package dependency: {rel}"

    forbidden_names = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        lower = path.name.lower()

        if any(
            token in lower
            for token in FORBIDDEN_NAME_TOKENS
        ):
            forbidden_names.append(
                str(path.relative_to(root))
            )

    assert not forbidden_names, (
        "Forbidden development filenames found: "
        + ", ".join(forbidden_names)
    )

    path_hits = []

    for path in root.rglob("*"):
        if (
            not path.is_file()
            or path.suffix.lower()
            not in {
                ".py",
                ".md",
                ".txt",
                ".toml",
                ".cff",
            }
        ):
            continue

        text = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        if WINDOWS_ABS_PATH.search(text):
            path_hits.append(
                str(path.relative_to(root))
            )

    assert not path_hits, (
        "Personal/local absolute paths found in public text files: "
        + ", ".join(path_hits)
    )

    print()
    print("Required-file whitelist       : PASS")
    print("Development-filename check    : PASS")
    print("Local-path check              : PASS")
    print("LICENSE STATUS                : MIT")
    print("PYTHON PUBLIC PACKAGE CHECK: PASS")


if __name__ == "__main__":
    main()
