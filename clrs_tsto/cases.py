from dataclasses import dataclass
import math


@dataclass(frozen=True)
class MissionCase:
    architecture: str
    ram_min: float
    scenario: str
    transition_start_mach: float
    transition_end_mach: float
    rocket2_mach: float
    performance_model: str


def build_case(
    architecture,
    ram_min,
    scenario,
    transition_end_mach,
    rocket2_mach,
):
    """
    Python equivalent of reference implementation V35B_0E_case.
    """

    architecture = str(architecture).upper()
    scenario = str(scenario).upper()

    if scenario not in ("LOW", "REFERENCE", "HIGH"):
        raise ValueError(
            "Performance scenario must be LOW, REFERENCE, or HIGH."
        )

    if not (2.3 <= float(ram_min) <= 3.0):
        raise ValueError(
            "ram_min must be between 2.3 and 3.0."
        )

    transition_start_mach = 6.0

    if architecture == "DMR":

        if abs(float(rocket2_mach) - 7.0) >= 1e-12:
            raise ValueError(
                "DMR requires rocket2_mach = 7.0."
            )

        if float(transition_end_mach) not in (6.5, 7.0):
            raise ValueError(
                "DMR transition_end_mach must be 6.5 or 7.0."
            )

        transition_end = float(transition_end_mach)

    elif architecture == "RAMJET_ONLY":

        if float(rocket2_mach) not in (6.0, 6.5, 7.0):
            raise ValueError(
                "RAMJET_ONLY rocket2_mach must be 6.0, 6.5, or 7.0."
            )

        transition_end = math.nan

    else:

        raise ValueError(
            "Architecture must be DMR or RAMJET_ONLY."
        )

    return MissionCase(
        architecture=architecture,
        ram_min=float(ram_min),
        scenario=scenario,
        transition_start_mach=transition_start_mach,
        transition_end_mach=transition_end,
        rocket2_mach=float(rocket2_mach),
        performance_model="V35B_0D_UNCERTAINTY_INTERFACE",
    )