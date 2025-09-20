import math
from typing import List


def pct_changes(prices: List[float]) -> List[float]:
    return [(prices[i] / prices[i - 1] - 1.0) for i in range(1, len(prices))]


def realized_vol_annualized(prices: List[float], bars_per_day: int = 288) -> float:
    rets = pct_changes(prices)
    if not rets:
        return float("nan")
    mu = sum(rets) / len(rets)
    var = sum((r - mu) ** 2 for r in rets) / max(1, len(rets) - 1)
    daily_vol = math.sqrt(var * bars_per_day)
    return daily_vol * math.sqrt(365.0)


def max_drawdown(prices: List[float]) -> float:
    if not prices:
        return float("nan")
    peak = prices[0]
    mdd = 0.0
    for p in prices:
        peak = max(peak, p)
        mdd = min(mdd, p / peak - 1.0)
    return abs(mdd)
