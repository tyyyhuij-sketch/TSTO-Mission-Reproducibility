import math


def atmosphere(Z_km):
    """
    Standard atmosphere model.

    Parameters
    ----------
    Z_km : float
        Geometric altitude [km]

    Returns
    -------
    P : float
        Pressure [Pa]

    T : float
        Temperature [K]
    """

    # geopotential altitude conversion
    H = Z_km / (1.0 + Z_km / 6356.766)

    Psl = 101325.0


    if Z_km < 11.0191:

        W = 1.0 - H / 44.3308

        T = 288.15 * W
        P = Psl * W ** 5.2559


    elif Z_km < 20.0631:

        W = math.exp((14.9647 - H) / 6.3416)

        T = 216.65
        P = Psl * 1.1953e-1 * W


    elif Z_km < 32.1619:

        W = 1.0 + (H - 24.9021) / 221.552

        T = 221.552 * W
        P = Psl * 2.5158e-2 * W ** (-34.1629)


    elif Z_km < 47.3501:

        W = 1.0 + (H - 39.7499) / 89.4107

        T = 250.35 * W
        P = Psl * 2.8338e-3 * W ** (-12.2011)


    else:

        W = math.exp((48.6252 - H) / 7.9223)

        T = 270.65
        P = Psl * 8.9155e-4 * W


    return P, T