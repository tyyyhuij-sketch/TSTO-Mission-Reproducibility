import numpy as np

from clrs_tsto.cases import build_case
from clrs_tsto.mission import evaluate_design
from clrs_tsto.optimizer import local_slsqp_polish


def _case21():
    return build_case(
        architecture="DMR",
        ram_min=2.5,
        scenario="REFERENCE",
        transition_end_mach=6.5,
        rocket2_mach=7.0,
    )


def test_slsqp_polish_from_frozen_point():
    case = _case21()

    frozen_x = np.asarray(
        [
            1.15357661420967,
            2.5,
            0.123042403208665,
        ],
        dtype=np.float64,
    )

    frozen = evaluate_design(
        frozen_x,
        case,
    )

    result = local_slsqp_polish(
        frozen_x,
        case,
    )

    assert np.isfinite(
        result.fun
    )

    assert result.fun <= (
        frozen.tog_w_t
        + 1e-8
    )

    polished = evaluate_design(
        result.x,
        case,
    )

    assert polished.valid
    assert polished.physical_pass

    assert result.x[0] <= (
        result.x[1]
        + 1e-10
    )


def test_frozen_point_is_in_expected_basin():
    case = _case21()

    d = evaluate_design(
        [
            1.15357661420967,
            2.5,
            0.123042403208665,
        ],
        case,
    )

    assert d.valid
    assert d.physical_pass
    assert abs(
        d.tog_w_t
        - 415.884533711041
    ) < 1e-8
