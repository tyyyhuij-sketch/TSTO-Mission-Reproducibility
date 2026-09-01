from clrs_tsto.cases import build_case
from clrs_tsto.mission import evaluate_design


CASE21_TOGW_T = 415.884533711041
CASE21_MCAT = 1.15357661420967
CASE21_MRAM_START = 2.5
CASE21_ALPHA = 0.123042403208665


def test_case21_frozen_design():

    case = build_case(
        architecture="DMR",
        ram_min=2.5,
        scenario="REFERENCE",
        transition_end_mach=6.5,
        rocket2_mach=7.0,
    )

    result = evaluate_design(
        [
            CASE21_MCAT,
            CASE21_MRAM_START,
            CASE21_ALPHA,
        ],
        case,
    )

    print()
    print("=== PY-5B Case-21 frozen design ===")
    print("Message =", result.message)
    print("TOGW =", result.tog_w_t, "t")
    print("Hram,start =", result.h_ram_start_km, "km")
    print("MuTot1 =", result.mu_tot1)
    print("MuTot2 =", result.mu_tot2)

    assert result.valid
    assert result.physical_pass

    assert abs(
        result.tog_w_t
        - CASE21_TOGW_T
    ) < 1e-8

    assert abs(
        result.h_ram_start_km
        - 15.0
    ) < 1e-10
