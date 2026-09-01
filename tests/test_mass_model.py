import math

from clrs_tsto.mass_model import (
    segment_mass_ratio,
    two_stage_mass_closure,
)


def test_segment_mass_ratio_basic():
    mu = segment_mass_ratio(
        delta_v_mps=300.0,
        gravity_loss_mps=20.0,
        isp_s=341.0,
    )

    expected = math.exp(
        (300.0 + 20.0)
        /
        (9.81 * 341.0)
    )

    assert abs(mu - expected) < 1e-15


def test_mass_closure_uses_exactly_ten_iterations():
    result = two_stage_mass_closure(
        m_load=8.0,
        sigma1st_rbcc=0.42,
        sigma2nd=0.238,
        mu_tot1=1.4,
        mu_tot2=2.0,
        ma_takeoff=1.15357661420967,
        h_takeoff_km=0.0,
    )

    assert result.iterations == 10
    assert result.total_mass_t > 0.0
    assert result.first_stage_mass_t > 0.0
    assert result.second_stage_mass_t > 0.0
