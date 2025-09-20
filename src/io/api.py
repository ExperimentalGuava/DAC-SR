from fastapi import FastAPI, HTTPException
from ..datasource.market import fetch_ohlcv
from .config import load_config
from ..engine.builder import build_snapshot


app = FastAPI(title="DAC Stability Rating (SR) API", version="1.0.0")


@app.get("/v1/sr/{asset}")
async def get_sr(asset: str):
    asset_u = asset.upper()
    if asset_u not in ("BTC", "ETH"):
        raise HTTPException(status_code=400, detail="Unsupported asset. Use BTC or ETH.")

    cfg = load_config()  # reads config/v1/weights.yaml
    market = await fetch_ohlcv(asset_u)

    snap  =  await build_snapshot(
        asset=asset_u,
        market=market,
        knees=cfg["knees"],
        weights=cfg["components"],
        schema_version=cfg["schema_version"],
    )

    return {
        "asset": snap.asset,
        "timestamp": snap.ts.isoformat(),
        "sr": round(snap.sr, 2),
        "components": [
            {
                "name": c.name,
                "score": round(c.score, 2),
                "weight": c.weight,
                "value": c.value,
                "meta": c.meta,
            }
            for c in snap.components
        ],
        "schema_version": snap.schema_version,
    }


@app.get("/v1/health")
async def health():
    return {"ok": True}
