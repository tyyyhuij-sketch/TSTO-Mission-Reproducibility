from clrs_tsto.atmosphere import atmosphere
from clrs_tsto.trajectory import flight_altitude, reference_altitude


def test_flight_altitude_M6():

    Ma = 6.0
    q_target = 95.8e3

    H = flight_altitude(Ma, q_target)

    P, T = atmosphere(H)

    q = 1.4 * P * Ma**2 / 2.0

    relative_error = abs(q - q_target) / q_target

    print()
    print("=== FlightAltitude M=6 check ===")
    print("Mach =", Ma)
    print("Altitude =", H, "km")
    print("Pressure =", P, "Pa")
    print("Temperature =", T, "K")
    print("Dynamic pressure =", q, "Pa")
    print("Relative error =", relative_error)

    assert relative_error < 1e-10


def test_reference_altitude_anchor():

    H = reference_altitude(2.5)

    print()
    print("=== Source anchor check ===")
    print("Mach = 2.5")
    print("Altitude =", H, "km")

    assert abs(H - 15.0) < 1e-10


def test_reference_trajectory():

    Mach = [2.3, 2.5, 3.0, 6.0, 6.5, 7.0]

    altitude = []
    dynamic_pressure_kPa = []

    print()
    print("=== Source-anchored trajectory check ===")

    for M in Mach:

        H = reference_altitude(M)

        P, _ = atmosphere(H)

        q = 1.4 * P * M**2 / 2.0

        altitude.append(H)
        dynamic_pressure_kPa.append(q / 1000.0)

        print(
            f"M = {M:.1f}, "
            f"H = {H:.12f} km, "
            f"q = {q / 1000.0:.12f} kPa"
        )

    assert abs(altitude[1] - 15.0) < 1e-10

    assert abs(dynamic_pressure_kPa[3] - 95.8) < 1e-6

    for i in range(len(altitude) - 1):
        assert altitude[i + 1] - altitude[i] >= -1e-10