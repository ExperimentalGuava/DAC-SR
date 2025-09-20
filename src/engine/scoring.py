def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


# Linear knee mapping for risk (higher is worse → lower score)
def inverse_risk_to_score(x: float, lo: float, hi: float) -> float:
    if x is None:
        return 50.0
    if x <= lo:
        return 100.0
    if x >= hi:
        return 0.0
    return 100.0 * (1.0 - (x - lo) / (hi - lo))


# Linear knee mapping for health (higher is better → higher score)
def direct_health_to_score(x: float, lo: float, hi: float) -> float:
    if x is None:
        return 50.0
    if x <= lo:
        return 0.0
    if x >= hi:
        return 100.0
    return 100.0 * ((x - lo) / (hi - lo))
