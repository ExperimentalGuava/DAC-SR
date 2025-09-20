from datetime import datetime
from ..engine.scoring import inverse_risk_to_score, direct_health_to_score
from ..indicators.volatility import realized_vol_annualized, max_drawdown
from ..models import ComponentScore, Snapshot
from ..datasource.market import fetch_orderbook
from ..datasource.onchain import fetch_onchain

async def build_snapshot(asset: str, market: dict, knees: dict, weights: dict, schema_version: str) -> Snapshot:
    closes, _ = market["closes"], market["vols"]
    # ---- VOL
    vol_a = realized_vol_annualized(closes)
    mdd = max_drawdown(closes)
    k_vol = knees[asset]["VOL"]
    S_vol_sigma = inverse_risk_to_score(vol_a, k_vol["sigma_lo"], k_vol["sigma_hi"])
    S_vol_mdd  = inverse_risk_to_score(mdd,   k_vol["mdd_lo"],   k_vol["mdd_hi"])
    S_VOL = (S_vol_sigma + S_vol_mdd) / 2.0

    # ---- LIQ
    ob = await fetch_orderbook(asset)
    spread = ob["spread_pct"]
    depth  = ob["depth_usd"]
    k_liq = knees[asset]["LIQ"]
    S_spread = inverse_risk_to_score(spread, k_liq["spread_lo"],   k_liq["spread_hi"])
    S_depth  = direct_health_to_score(depth, k_liq["depth10_lo"],  k_liq["depth10_hi"])
    S_LIQ = (S_spread + S_depth) / 2.0

    # ---- ONC
    oc = await fetch_onchain(asset)
    tx24   = oc["tx_24h"]
    addr24 = oc["active_addresses_24h"]
    feeptx = oc["fees_per_tx_usd"]

    k_onc = knees[asset]["ONC"]
    subscores = []
    if tx24 is not None:
        subscores.append(direct_health_to_score(tx24, k_onc["tx24h_lo"], k_onc["tx24h_hi"]))
    if addr24 is not None:
        subscores.append(direct_health_to_score(addr24, k_onc["addr24h_lo"], k_onc["addr24h_hi"]))
    if feeptx is not None:
        subscores.append(inverse_risk_to_score(feeptx, k_onc["fees_per_tx_usd_lo"], k_onc["fees_per_tx_usd_hi"]))
    S_ONC = sum(subscores)/len(subscores) if subscores else 50.0

    comps = [
        ComponentScore("VOL", S_VOL, weights["VOL"], value={"σ7a": vol_a, "MDD30": mdd}),
        ComponentScore("LIQ", S_LIQ, weights["LIQ"], value={"spread_pct": spread, "depth_usd": depth}),
        ComponentScore("DEC", 50.0,  weights["DEC"], value={}),
        ComponentScore("ONC", S_ONC, weights["ONC"], value={"tx_24h": tx24, "active_addresses_24h": addr24, "fees_per_tx_usd": feeptx}),
        ComponentScore("VAL", 50.0,  weights["VAL"], value={}),
    ]

    return Snapshot(ts=datetime.utcnow(), asset=asset.upper(), components=comps, schema_version=schema_version)
