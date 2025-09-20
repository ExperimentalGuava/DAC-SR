from src.engine.scoring import inverse_risk_to_score, direct_health_to_score, clamp


def test_clamp():
    assert clamp(5, 0, 10) == 5
    assert clamp(-1, 0, 10) == 0
    assert clamp(11, 0, 10) == 10


def test_inverse_risk_to_score_bounds():
    assert inverse_risk_to_score(0.2, 0.3, 1.2) == 100.0
    assert inverse_risk_to_score(1.3, 0.3, 1.2) == 0.0


def test_inverse_risk_to_score_linear():
    lo, hi = 0.3, 1.3
    mid = (lo + hi) / 2
    score_mid = inverse_risk_to_score(mid, lo, hi)
    assert 45.0 <= score_mid <= 55.0  # roughly around 50


def test_direct_health_to_score_bounds():
    assert direct_health_to_score(0.1, 0.2, 1.0) == 0.0
    assert direct_health_to_score(1.2, 0.2, 1.0) == 100.0


def test_direct_health_to_score_linear():
    lo, hi = 0.0, 10.0
    mid = 5.0
    score_mid = direct_health_to_score(mid, lo, hi)
    assert 45.0 <= score_mid <= 55.0
