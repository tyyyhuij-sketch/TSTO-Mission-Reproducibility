from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator


RAMJET_REQUIRED_COLUMNS = [
    "Mach",
    "RAMJET_LOW_s",
    "RAMJET_REFERENCE_s",
    "RAMJET_HIGH_s",
]

TRANSITION_REQUIRED_COLUMNS = [
    "Scenario",
    "TransitionEndMach",
    "Mach",
    "BlendedI_s",
]


def _data_directory():
    """
    Return the repository propulsion-data directory.
    """

    project_root = Path(__file__).resolve().parents[1]

    return project_root / "data" / "propulsion"


def _read_required_csv(file_path, required_columns):
    """
    Python equivalent of V35B_0E_readtable.
    """

    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(
            f"Missing input file: {file_path}"
        )

    table = pd.read_csv(file_path)

    missing = [
        column
        for column in required_columns
        if column not in table.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns in {file_path}: "
            + ", ".join(missing)
        )

    return table


@lru_cache(maxsize=1)
def _load_propulsion_tables():

    data_dir = _data_directory()

    ramjet = _read_required_csv(
        data_dir / "V35B_0D_RAMJET_SCENARIOS.csv",
        RAMJET_REQUIRED_COLUMNS,
    )

    transition = _read_required_csv(
        data_dir / "V35B_0D_TRANSITION_BLEND_SCENARIOS.csv",
        TRANSITION_REQUIRED_COLUMNS,
    )

    # Explicit float64 conversion for all numerical model inputs.
    for column in RAMJET_REQUIRED_COLUMNS:
        ramjet[column] = pd.to_numeric(
            ramjet[column],
            errors="raise",
        ).astype(np.float64)

    transition["Scenario"] = (
        transition["Scenario"]
        .astype(str)
        .str.upper()
    )

    for column in [
        "TransitionEndMach",
        "Mach",
        "BlendedI_s",
    ]:
        transition[column] = pd.to_numeric(
            transition[column],
            errors="raise",
        ).astype(np.float64)

    return ramjet, transition


def _pchip_value(x, y, query):
    """
    Evaluate reference-equivalent PCHIP without permitting extrapolation.
    """

    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    query = np.float64(query)

    if x.ndim != 1 or y.ndim != 1:
        raise ValueError("PCHIP input arrays must be one-dimensional.")

    if len(x) != len(y):
        raise ValueError("PCHIP x and y arrays must have equal length.")

    if not np.all(np.diff(x) > 0.0):
        raise ValueError(
            "Source Mach points must be strictly increasing."
        )

    if query < x[0] or query > x[-1]:
        raise ValueError(
            "PCHIP extrapolation is forbidden."
        )

    interpolator = PchipInterpolator(
        x,
        y,
        extrapolate=False,
    )

    value = interpolator(query)

    return float(value)


def performance_at(M, case):
    """
    Python equivalent of reference implementation V35B_0E_performance_at.

    Parameters
    ----------
    M : float
        Mach number.

    case : MissionCase
        Architecture/performance case.

    Returns
    -------
    Ieff : float
        Effective specific impulse [s].
    """

    M = float(M)

    ramjet, transition = _load_propulsion_tables()

    scenario = case.scenario.upper()

    if scenario == "LOW":
        column = "RAMJET_LOW_s"

    elif scenario == "REFERENCE":
        column = "RAMJET_REFERENCE_s"

    elif scenario == "HIGH":
        column = "RAMJET_HIGH_s"

    else:
        raise ValueError(
            "Unknown performance scenario."
        )

    # ------------------------------------------------------------
    # DMR architecture
    # ------------------------------------------------------------

    if case.architecture == "DMR":

        if M <= 6.0 + 1e-12:

            minimum_mach = float(ramjet["Mach"].min())

            if M < minimum_mach - 1e-12:
                raise ValueError(
                    "Ramjet performance extrapolation "
                    "below M=2.3 is forbidden."
                )

            Ieff = _pchip_value(
                ramjet["Mach"].to_numpy(),
                ramjet[column].to_numpy(),
                M,
            )

        else:

            mask = (
                (transition["Scenario"] == scenario)
                &
                (
                    np.abs(
                        transition["TransitionEndMach"]
                        - case.transition_end_mach
                    )
                    < 1e-10
                )
            )

            subset = transition.loc[mask]

            if subset.empty:
                raise ValueError(
                    "Missing transition scenario."
                )

            max_mach = float(subset["Mach"].max())

            if M > max_mach + 1e-12:
                raise ValueError(
                    "DMR performance extrapolation "
                    "above M7 is forbidden."
                )

            Ieff = _pchip_value(
                subset["Mach"].to_numpy(),
                subset["BlendedI_s"].to_numpy(),
                M,
            )

    # ------------------------------------------------------------
    # RAMJET_ONLY architecture
    # ------------------------------------------------------------

    elif case.architecture == "RAMJET_ONLY":

        if M <= 6.0 + 1e-12:

            minimum_mach = float(ramjet["Mach"].min())

            if M < minimum_mach - 1e-12:
                raise ValueError(
                    "Ramjet performance extrapolation "
                    "below M=2.3 is forbidden."
                )

            Ieff = _pchip_value(
                ramjet["Mach"].to_numpy(),
                ramjet[column].to_numpy(),
                M,
            )

        else:

            if M > 7.0 + 1e-12:
                raise ValueError(
                    "Reviewer-comparator continuation "
                    "is forbidden beyond M7."
                )

            values_M4 = ramjet.loc[
                np.abs(ramjet["Mach"] - 4.0) < 1e-10,
                column,
            ]

            values_M6 = ramjet.loc[
                np.abs(ramjet["Mach"] - 6.0) < 1e-10,
                column,
            ]

            if len(values_M4) != 1 or len(values_M6) != 1:
                raise ValueError(
                    "Exactly one M4 and one M6 "
                    "ramjet reference value are required."
                )

            v4 = float(values_M4.iloc[0])
            v6 = float(values_M6.iloc[0])

            slope = (v6 - v4) / (6.0 - 4.0)

            Ieff = v6 + slope * (M - 6.0)

    else:

        raise ValueError(
            "Unknown architecture."
        )

    if not np.isfinite(Ieff) or Ieff <= 0.0:
        raise ValueError(
            "Invalid uncertainty-interface performance value."
        )

    return float(Ieff)