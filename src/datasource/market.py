import httpx
import ssl
import certifi

SYMBOLS = {"BTC": "BTCUSDT", "ETH": "ETHUSDT"}


async def fetch_ohlcv(
    asset: str,
    interval: str = "5m",
    limit: int = 500,
    base_url: str = "https://api.binance.com",
) -> dict:
    """
    Fetch OHLCV data from Binance.
    Returns a dict with 'closes' and 'vols' lists.
    """
    asset_u = asset.upper()
    symbol = SYMBOLS.get(asset_u)
    if not symbol:
        raise ValueError(f"Unsupported asset: {asset}")

    url = f"{base_url}/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}

    ssl_context = ssl.create_default_context(cafile=certifi.where())

    try:
        async with httpx.AsyncClient(verify=ssl_context, timeout=20.0) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            raw = r.json()
    except Exception as e:
        raise RuntimeError(f"Market fetch failed: {e}") from e

    # Binance returns kline arrays; index 4 = close, index 5 = volume
    closes = [float(x[4]) for x in raw]
    vols = [float(x[5]) for x in raw]
    if not closes or not vols:
        raise RuntimeError("Market fetch returned empty data.")

    return {"closes": closes, "vols": vols}

async def fetch_orderbook(
    asset: str,
    limit: int = 50,
    base_url: str = "https://api.binance.com",
) -> dict:
    """
    Fetch order book snapshot from Binance.
    Returns best bid/ask spread % and depth within 1% of mid-price.
    """
    asset_u = asset.upper()
    symbol = SYMBOLS.get(asset_u)
    if not symbol:
        raise ValueError(f"Unsupported asset: {asset}")

    url = f"{base_url}/api/v3/depth"
    params = {"symbol": symbol, "limit": limit}

    ssl_context = ssl.create_default_context(cafile=certifi.where())
    async with httpx.AsyncClient(verify=ssl_context, timeout=20.0) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        raw = r.json()

    bids = [(float(p), float(q)) for p, q in raw["bids"]]
    asks = [(float(p), float(q)) for p, q in raw["asks"]]
    if not bids or not asks:
        raise RuntimeError("Orderbook returned empty")

    best_bid = bids[0][0]
    best_ask = asks[0][0]
    mid = (best_bid + best_ask) / 2
    spread_pct = (best_ask - best_bid) / mid

    # Depth within ±1% of mid
    lower_bound, upper_bound = mid * 0.99, mid * 1.01
    depth = sum(q * p for p, q in bids if p >= lower_bound)
    depth += sum(q * p for p, q in asks if p <= upper_bound)

    return {"spread_pct": spread_pct, "depth_usd": depth}
