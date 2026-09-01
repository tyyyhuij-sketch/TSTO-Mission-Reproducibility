from clrs_tsto.cases import build_case
from clrs_tsto.mission_nodes import build_airbreathing_nodes


def test_case21_node_endpoints_and_modes():
    case = build_case(
        architecture="DMR",
        ram_min=2.5,
        scenario="REFERENCE",
        transition_end_mach=6.5,
        rocket2_mach=7.0,
    )

    result = build_airbreathing_nodes(
        2.5,
        case,
    )

    assert abs(result.mach[0] - 2.5) < 1e-15
    assert abs(result.mach[-1] - 7.0) < 1e-15

    assert "RAMJET" in result.segment_modes
    assert "DMR_BLEND" in result.segment_modes
    assert "SCRAMJET" in result.segment_modes


def test_offgrid_start_is_preserved():
    case = build_case(
        architecture="DMR",
        ram_min=2.5,
        scenario="REFERENCE",
        transition_end_mach=6.5,
        rocket2_mach=7.0,
    )

    result = build_airbreathing_nodes(
        2.53,
        case,
    )

    assert abs(result.mach[0] - 2.53) < 1e-15
    assert result.mach[1] >= 2.6 - 1e-14
