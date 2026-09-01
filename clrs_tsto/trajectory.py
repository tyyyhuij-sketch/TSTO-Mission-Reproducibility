from clrs_tsto.atmosphere import atmosphere
from clrs_tsto.config import DEFAULT_TRAJECTORY_CONFIG


def flight_altitude(Ma, Pd, Gamma=1.4):

    """
    Calculate altitude from Mach number
    and target dynamic pressure.

    Parameters
    ----------
    Ma : float
        Mach number

    Pd : float
        Target dynamic pressure [Pa]

    Gamma : float
        Specific heat ratio

    Returns
    -------
    H : float
        Altitude [km]
    """

    HH = 200.0
    HL = 0.0

    error = 1.0


    while abs(error) > 1e-10:

        H = 0.5 * (HH + HL)

        P, T = atmosphere(H)

        q = Gamma * P * Ma ** 2 / 2.0

        error = (q - Pd) / Pd


        if error < 0:

            HH = H

        else:

            HL = H


    return H

def reference_altitude(M, cfg=DEFAULT_TRAJECTORY_CONFIG):
    """
    Source-anchored Mach-altitude trajectory.

    reference-equivalent:
        Step3R2D_reference_altitude

    Parameters
    ----------
    M : float
        Mach number.

    cfg : TrajectoryConfig
        Frozen trajectory configuration.

    Returns
    -------
    H : float
        Geometric altitude [km].
    """

    Pd = cfg.HighMachReferenceDynamicPressure_Pa

    H6 = flight_altitude(
        cfg.HighMachStartMach,
        Pd
    )

    if M < cfg.HighMachStartMach - 1e-12:

        H = (
            cfg.LowMidAnchorAltitude_km
            +
            (M - cfg.LowMidAnchorMach)
            /
            (cfg.HighMachStartMach - cfg.LowMidAnchorMach)
            *
            (H6 - cfg.LowMidAnchorAltitude_km)
        )

    else:

        H = flight_altitude(
            M,
            Pd
        )

    return H