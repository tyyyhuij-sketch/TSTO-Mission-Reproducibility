from clrs_tsto.cases import build_case
from clrs_tsto.propulsion import (
    _load_propulsion_tables,
    performance_at,
)


def test_propulsion_csv_loading():

    ramjet, transition = _load_propulsion_tables()

    print()
    print("=== Propulsion CSV loading check ===")

    print("Ramjet rows =", len(ramjet))
    print("Transition rows =", len(transition))

    print()
    print("Ramjet columns:")
    print(list(ramjet.columns))

    print()
    print("Transition columns:")
    print(list(transition.columns))

    assert len(ramjet) > 0
    assert len(transition) > 0


def test_case21_propulsion_interface_basic():

    case = build_case(
        architecture="DMR",
        ram_min=2.5,
        scenario="REFERENCE",
        transition_end_mach=6.5,
        rocket2_mach=7.0,
    )

    Mach = [
        2.5,
        4.35,
        6.0,
        6.25,
        6.75,
    ]

    print()
    print("=== Case-21 propulsion interface ===")

    for M in Mach:

        Ieff = performance_at(
            M,
            case,
        )

        print(
            f"M = {M:.2f}, "
            f"Ieff = {Ieff:.15f} s"
        )

        assert Ieff > 0.0