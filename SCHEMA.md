# Stability Rating (SR) — v1 Calculation Spec


## Assets
Initial coverage: BTC, ETH (extendable).


## Update Cadence
5–10 minute snapshots, with rolling 24h and 7d aggregates.


## Components & Weights
Weights default to equal (0.20 each). Calibrated per release.
1. Market Volatility (VOL)
2. Liquidity & Microstructure (LIQ)
3. Decentralisation / Concentration (DEC)
4. On‑chain Activity & Demand (ONC)
5. Validator / Hashrate Stability (VAL)


## Metric Definitions (v1)
### 1) Market Volatility (VOL)
- 7‑day realized volatility (annualized) on 5‑min bars: `σ7a`
- 30‑day max drawdown on closes: `MDD30`
- Score mapping (risk inverse):
- `S_volσ = 100 * (1 - clamp((σ7a - σ_lo) / (σ_hi - σ_lo), 0, 1))`
- `S_volmdd = 100 * (1 - clamp((MDD30 - d_lo) / (d_hi - d_lo), 0, 1))`
- `S_VOL = mean(S_volσ, S_volmdd)`


### 2) Liquidity & Microstructure (LIQ)
- Median top‑of‑book spread %: `Spread%`
- Cumulative depth within 10bp (USD): `Depth10`
- Slippage for a $100k market order (absolute %): `Slip100k`
- Score mapping (higher depth / lower spread & slippage is better):
- `S_liq = 100 * mean( z+(Depth10), z+(1/Spread%), z+(1/Slip100k) )` with robust scaling.


### 3) Decentralisation / Concentration (DEC)
- Holdings HHI over top‑k addresses/UTXO: `HHI_k`
- Gini of holdings: `Gini`
- Exchange‑held float %: `ExFloat%`
- Score mapping (lower concentration is better):
- `S_DEC = 100 * mean( z+(1/HHI_k), z+(1/Gini), z+(1/ExFloat%) )`


### 4) On‑chain Activity & Demand (ONC)
- Tx/s EMA trend: `ΔEMA_tx = EMA30 – EMA90`
- Active addresses trend: `ΔEMA_addr = EMA30 – EMA90`
- Fees per tx (proxy for congestion/demand): `FeesPerTx`
- Realized cap ratio (price/realized price): `RC`
- Score mapping:
- `S_ONC = 100 * mean( z+(ΔEMA_tx), z+(ΔEMA_addr), z+(1/FeesPerTx), z+(1/RC) )`


### 5) Validator / Hashrate Stability (VAL)
- 30d hashrate/validator count variance: `VarHash`
- Client / pool diversity index (0–1): `DivIdx`
- Orphan / reorg rate (per 10k blocks): `ReorgRate`
- Score mapping:
- `S_VAL = 100 * mean( z+(1/VarHash), z+(DivIdx), z+(1/ReorgRate) )`


## Aggregation
`SR = Σ_i w_i * S_i`, i ∈ {VOL, LIQ, DEC, ONC, VAL}


## Output Payload (JSON)
```json
{
"asset": "BTC",
"timestamp": "2025-09-03T09:00:00Z",
"sr": 81.42,
"components": [
{"name":"VOL","score":73.1,"weight":0.2,"value":{"σ7a":0.54,"MDD30":0.18}},
{"name":"LIQ","score":86.2,"weight":0.2,"value":{"Spread%":0.003,"Depth10":2450000,"Slip100k":0.0012}},
{"name":"DEC","score":65.7,"weight":0.2,"value":{"HHI_k":0.12,"Gini":0.76,"ExFloat%":6.1}},
{"name":"ONC","score":84.0,"weight":0.2,"value":{"ΔEMA_tx":1.1,"ΔEMA_addr":0.9,"FeesPerTx":2.1,"RC":1.3}},
{"name":"VAL","score":98.1,"weight":0.2,"value":{"VarHash":0.002,"DivIdx":0.78,"ReorgRate":0.3}}
],
"schema_version": "1.0.0",
"run_id": "2025-09-03T09:00:00Z/btc/ab12"
}