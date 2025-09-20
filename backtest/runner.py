# backtest/runner.py
import pandas as pd
from ..src.engine.scoring import inverse_risk_to_score
from ..src.indicators.volatility import realized_vol_annualized

def daily_sr(prices_5m: pd.Series) -> pd.Series:
    # resample → compute SR once per day
    # (demo: only volatility component)
    def _sr(day_prices):
        vol = realized_vol_annualized(day_prices.tolist())
        return inverse_risk_to_score(vol, knee=(0.3, 1.2))
    return prices_5m.groupby(prices_5m.index.date).apply(lambda s: _sr(s.values))
