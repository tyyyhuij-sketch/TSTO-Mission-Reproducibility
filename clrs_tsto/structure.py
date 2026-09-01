from clrs_tsto.atmosphere import atmosphere


GAMMA = 1.4


def frame_mass_coefficient(
    m_tot,
    ma_takeoff_cars,
    z_takeoff_cars,
    sigma1st_rbcc,
):
    """
    Scientific-equivalent port of reference implementation FrameMassCoefficient.

    Important
    ---------
    This function intentionally preserves the frozen reference implementation arithmetic and
    calling convention exactly. No unit reinterpretation or model correction
    is applied here.

    Parameters
    ----------
    m_tot : float
        Mass quantity passed by the frozen mission solver.
    ma_takeoff_cars : float
        Electromagnetic-release Mach number.
    z_takeoff_cars : float
        Release altitude [km].
    sigma1st_rbcc : float
        Baseline first-stage structural fraction.

    Returns
    -------
    sigma1st_cars : float
        Corrected first-stage structural fraction.
    ratio_ld : float
        Inferred reference length-to-diameter ratio.
    """

    Ke = 1.24
    Kin = 1.25

    m_frame_rbcc = m_tot * sigma1st_rbcc

    # Frozen RBCC reference points used by the reference implementation structural correction.
    ma_takeoff_rbcc = 0.1
    z_takeoff_rbcc = 0.0
    p_takeoff_rbcc, _ = atmosphere(z_takeoff_rbcc)
    q_takeoff_rbcc = (
        GAMMA
        * p_takeoff_rbcc
        * ma_takeoff_rbcc**2
        / 2.0
    )

    ma_ram_start_rbcc = 2.5
    z_ram_start_rbcc = 15.0
    p_ram_start_rbcc, _ = atmosphere(z_ram_start_rbcc)
    q_ram_start_rbcc = (
        GAMMA
        * p_ram_start_rbcc
        * ma_ram_start_rbcc**2
        / 2.0
    )

    ma_scram_start_rbcc = 6.0
    z_scram_start_rbcc = 22.5
    p_scram_start_rbcc, _ = atmosphere(z_scram_start_rbcc)
    q_scram_start_rbcc = (
        GAMMA
        * p_scram_start_rbcc
        * ma_scram_start_rbcc**2
        / 2.0
    )

    p_takeoff_cars, _ = atmosphere(z_takeoff_cars)
    q_takeoff_cars = (
        GAMMA
        * p_takeoff_cars
        * ma_takeoff_cars**2
        / 2.0
    )

    q_max_rbcc = max(
        max(q_takeoff_rbcc, q_ram_start_rbcc),
        q_scram_start_rbcc,
    )

    ratio_ld = (
        m_frame_rbcc
        /
        (
            6.3995
            * Ke
            * (Kin**1.42)
            * ((q_max_rbcc / 1000.0) ** 0.283)
            * ((m_tot / 1000.0) ** 0.95)
        )
    ) ** (1.0 / 0.71)

    m_frame_cars = (
        6.3995
        * Ke
        * (Kin**1.42)
        * ((q_takeoff_cars / 1000.0) ** 0.283)
        * ((m_tot / 1000.0) ** 0.95)
        * (ratio_ld**0.71)
    )

    sigma1st_cars = m_frame_cars / m_tot

    if sigma1st_cars < sigma1st_rbcc:
        sigma1st_cars = sigma1st_rbcc

    return float(sigma1st_cars), float(ratio_ld)
