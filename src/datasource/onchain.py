import os, httpx, ssl, certifi
from typing import Optional, Dict, Any

BLOCKCHAIR = {
    "BTC": "https://api.blockchair.com/bitcoin/stats",
    "ETH": "https://api.blockchair.com/ethereum/stats",
}
ETHERSCAN_API = "https://api.etherscan.io/api"

def _to_int(x): 
    try: return int(x)
    except: return None

def _to_float(x):
    try: return float(x)
    except: return None

async def _fetch_blockchair(asset: str, client: httpx.AsyncClient) -> Dict[str, Any]:
    url = BLOCKCHAIR.get(asset.upper())
    if not url: raise ValueError(f"Unsupported asset: {asset}")
    r = await client.get(url); r.raise_for_status()
    js = r.json(); data = js.get("data", {}) if isinstance(js, dict) else {}
    tx_24h = data.get("transactions_24h") or data.get("transactions_24hrs") or data.get("transactions_24h_count")
    active_24h = data.get("addresses_active_24h") or data.get("active_addresses_24h") or data.get("active_addresses_recent")
    fees_total_usd = data.get("fees_24h_usd") or data.get("transaction_fees_24h_usd") or data.get("fees_last_24h_usd")
    fees_per_tx_usd = None
    try:
        if fees_total_usd and tx_24h:
            fees_per_tx_usd = float(fees_total_usd) / float(tx_24h)
    except: pass
    return {
        "tx_24h": _to_int(tx_24h),
        "active_addresses_24h": _to_int(active_24h),
        "fees_per_tx_usd": _to_float(fees_per_tx_usd),
    }

async def _fetch_etherscan_eth_fallback(client: httpx.AsyncClient) -> Dict[str, Optional[float]]:
    api_key = os.getenv("ETHERSCAN_API_KEY")
    if not api_key:
        return {"tx_24h": None, "active_addresses_24h": None, "fees_per_tx_usd": None}
    try:
        tx_url = f"{ETHERSCAN_API}?module=stats&action=dailytx&startdate=2025-01-01&enddate=2025-12-31&sort=asc&apikey={api_key}"
        r1 = await client.get(tx_url); r1.raise_for_status()
        tx_series = (r1.json() or {}).get("result", [])
        tx_24h = _to_int(tx_series[-1].get("transactionCount")) if tx_series else None

        gas_url = f"{ETHERSCAN_API}?module=gastracker&action=gasoracle&apikey={api_key}"
        r2 = await client.get(gas_url); r2.raise_for_status()
        gas_gwei = _to_float((r2.json().get("result") or {}).get("ProposeGasPrice"))

        price_url = "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT"
        r3 = await client.get(price_url); r3.raise_for_status()
        eth_usd = _to_float((r3.json() or {}).get("price"))

        fees_per_tx_usd = None
        AVG_GAS_PER_TX = 100_000
        if gas_gwei is not None and eth_usd is not None:
            fees_per_tx_usd = gas_gwei * AVG_GAS_PER_TX * 1e-9 * eth_usd

        return {"tx_24h": tx_24h, "active_addresses_24h": None, "fees_per_tx_usd": fees_per_tx_usd}
    except:
        return {"tx_24h": None, "active_addresses_24h": None, "fees_per_tx_usd": None}

async def fetch_onchain(asset: str) -> dict:
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    async with httpx.AsyncClient(verify=ssl_ctx, timeout=20.0) as client:
        primary = await _fetch_blockchair(asset, client)
        if asset.upper() == "BTC":
            return primary
        if (asset.upper() == "ETH"
            and primary.get("tx_24h") is None
            and primary.get("active_addresses_24h") is None
            and primary.get("fees_per_tx_usd") is None):
            fallback = await _fetch_etherscan_eth_fallback(client)
            for k, v in fallback.items():
                if v is not None:
                    primary[k] = v
        return primary
