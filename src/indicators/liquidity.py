def turnover_ratio(vols: list, prices: list) -> float:
    # crude: notional volume / market cap proxy unavailable => use relative
    notional = sum(v*p for v, p in zip(vols, prices[-len(vols):]))
    price_var = max(prices) - min(prices)
    return notional / (1.0 + price_var)
