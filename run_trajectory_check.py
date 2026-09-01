from clrs_tsto.atmosphere import atmosphere
from clrs_tsto.trajectory import reference_altitude


GAMMA = 1.4


def main():
    mach_values = [
        2.3,
        2.5,
        3.0,
        6.0,
        6.5,
        7.0,
    ]

    rows = []

    for mach in mach_values:
        altitude_km = reference_altitude(mach)
        pressure_pa, _ = atmosphere(altitude_km)
        q_kpa = (
            GAMMA
            * pressure_pa
            * mach**2
            / 2.0
            / 1000.0
        )

        rows.append(
            (mach, altitude_km, q_kpa)
        )

    print()
    print("=== FINAL PYTHON SOURCE-ANCHORED TRAJECTORY AUDIT ===")
    print("Mach        Altitude_km      DynamicPressure_kPa")

    for mach, altitude_km, q_kpa in rows:
        print(
            f"{mach:4.1f}        "
            f"{altitude_km:12.9f}      "
            f"{q_kpa:16.9f}"
        )

    h25 = next(
        h for m, h, q in rows
        if m == 2.5
    )

    q6 = next(
        q for m, h, q in rows
        if m == 6.0
    )

    altitudes = [
        h
        for m, h, q in rows
    ]

    assert abs(h25 - 15.0) < 1e-10
    assert abs(q6 - 95.8) < 1e-6

    for a, b in zip(
        altitudes[:-1],
        altitudes[1:],
    ):
        assert b - a >= -1e-10

    print("FINAL PYTHON SOURCE-ANCHORED TRAJECTORY AUDIT: PASS")


if __name__ == "__main__":
    main()
