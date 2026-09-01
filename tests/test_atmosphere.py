from clrs_tsto.atmosphere import atmosphere


def test_atmosphere_15km():

    P, T = atmosphere(15)

    print("Altitude = 15 km")
    print("Pressure =", P, "Pa")
    print("Temperature =", T, "K")

    assert abs(T - 216.65) < 1e-6