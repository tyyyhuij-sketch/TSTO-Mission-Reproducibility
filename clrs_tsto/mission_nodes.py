import math
from dataclasses import dataclass

import numpy as np

from clrs_tsto.trajectory import reference_altitude


D_MACH = 0.1


@dataclass(frozen=True)
class AirbreathingNodes:
    mach: np.ndarray
    altitude_km: np.ndarray
    segment_modes: tuple[str, ...]


def _colon_positive(start, step, stop):
    """
    Construct the positive-step sequence needed for the frozen reference implementation form:

        start:step:stop

    the reference implementation's colon operator treats an endpoint that is reached within
    floating-point round-off as the exact requested stop. We reproduce that
    endpoint behavior explicitly so that the later reference implementation-style
    unique([MramStart Mtail Rocket2Mach]) does not create a spurious duplicate.
    """

    start = float(start)
    step = float(step)
    stop = float(stop)

    if not all(math.isfinite(v) for v in (start, step, stop)):
        raise ValueError("Colon inputs must be finite.")

    if step <= 0.0:
        raise ValueError("This frozen mission helper requires step > 0.")

    if start > stop:
        return np.asarray([], dtype=np.float64)

    n = int(math.floor((stop - start) / step + 1e-12))

    values = np.asarray(
        [start + k * step for k in range(n + 1)],
        dtype=np.float64,
    )

    values = values[values <= stop + 1e-12]

    # Critical reference implementation-equivalence detail:
    # Example: 2.4 + 41*0.1 can be 6.500000000000001 in Python.
    # the reference implementation's colon endpoint is effectively 6.5 here. Snap only the final
    # value when it is within the frozen numerical tolerance.
    if len(values) > 0 and abs(float(values[-1]) - stop) <= 1e-12:
        values[-1] = np.float64(stop)

    return values


def _unique_sorted(values):
    """
    Equivalent behavior needed here for the reference sequence:
        unique(...)
        sort(...)

    After reference implementation-colon endpoint handling above, exact duplicates are removed.
    """

    values = np.asarray(values, dtype=np.float64)

    if values.ndim != 1:
        raise ValueError("Mach nodes must be one-dimensional.")

    return np.unique(values)


def build_airbreathing_nodes(mram_start, case, d_mach=D_MACH):
    """
    Scientific-equivalent port of reference implementation
    Step3R2D_build_airbreathing_nodes.
    """

    mram_start = float(mram_start)
    d_mach = float(d_mach)

    # reference implementation:
    # Mtail=(ceil((MramStart+1e-9)/dMa)*dMa):dMa:c.Rocket2Mach;
    tail_start = math.ceil(
        (mram_start + 1e-9) / d_mach
    ) * d_mach

    m_tail = _colon_positive(
        tail_start,
        d_mach,
        case.rocket2_mach,
    )

    # reference implementation:
    # M=unique([MramStart Mtail c.Rocket2Mach]);
    # M=sort(M);
    combined = np.concatenate(
        (
            np.asarray([mram_start], dtype=np.float64),
            m_tail,
            np.asarray([case.rocket2_mach], dtype=np.float64),
        )
    )

    mach = _unique_sorted(combined)

    altitude_km = np.asarray(
        [reference_altitude(m) for m in mach],
        dtype=np.float64,
    )

    segment_modes = []

    for k in range(len(mach) - 1):

        midpoint_mach = 0.5 * (
            float(mach[k])
            + float(mach[k + 1])
        )

        if case.architecture == "RAMJET_ONLY":

            mode = "RAMJET"

        else:

            if midpoint_mach < 6.0:
                mode = "RAMJET"

            elif midpoint_mach < case.transition_end_mach:
                mode = "DMR_BLEND"

            else:
                mode = "SCRAMJET"

        segment_modes.append(mode)

    return AirbreathingNodes(
        mach=mach,
        altitude_km=altitude_km,
        segment_modes=tuple(segment_modes),
    )
