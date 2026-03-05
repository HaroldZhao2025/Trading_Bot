````md
# Trading_Bot (Olares-ready Algorithm)

This repo packages a **Freqtrade-based trading engine** as an “Algorithm” runtime (containerized) and ships a **strategy pack** + **multi-exchange configs**.  
It also includes a lightweight **DEX vs CEX arb scanner** (`FT_CMD=arb-scan`) with a DEX fallback source.

---

## Project layout

- `user_data/strategies/` — strategy pack (bots)
- `config/` — exchange configs (one exchange per instance)
- `offline_validate.py` — offline validation for strategies (no exchange required)
- `docker-compose.yml` — run multiple exchange instances locally (mirrors Olares multi-instance)
- `entrypoint.sh` — container entrypoint (`trade` by default, `arb-scan` optional)
- `olares/` — Olares-specific helpers (arb scanner + adapters)

---

## Strategies (8)

- `GridSimple`
- `MartingaleGuarded`
- `CtaTrend`
- `DcaAccumulator`
- `DonchianBreakout`
- `BollingerMR`
- `RsiMeanReversion`
- `AtrBreakout`

---

## Quick start (local)

### 1) Build image
```bash
docker build -t otomic-algo:local .
````

### 2) Offline validate strategies (no exchange access)

```bash
docker run --rm -it \
  -v "$(pwd)/offline_validate.py:/freqtrade/offline_validate.py" \
  -w /freqtrade \
  otomic-algo:local \
  python /freqtrade/offline_validate.py
```

You should see `[OK]` lines for all strategies.

---

## Run multi-exchange instances (docker compose)

> One exchange per process. Multiple exchanges = multiple instances.

```bash
docker compose up -d
docker compose ps
```

Health checks:

```bash
curl -s -o /dev/null -w "kraken:%{http_code}\n"   http://localhost:8080
curl -s -o /dev/null -w "coinbase:%{http_code}\n" http://localhost:8081
curl -s -o /dev/null -w "bitstamp:%{http_code}\n" http://localhost:8083
```

Stop:

```bash
docker compose down
```

Notes:

* Some exchanges may be blocked depending on your network/region (e.g., CDN/CloudFront). Swap to a reachable exchange config.
* Coinbase in this setup uses `use_order_book: false` because orderbook may not be available in the CCXT/Freqtrade integration.

---

## DEX vs CEX arb scanner (demo)

This mode compares:

* CEX mid price via **CCXT** (e.g., Kraken `ETH/USD`)
* DEX side via **0x v2 quote** (if `ZEROX_API_KEY` provided) with fallback to **DexScreener** (no key)

### Run arb-scan

```bash
docker run --rm -it \
  -e FT_CMD=arb-scan \
  -e ARB_CEX_EXCHANGE=kraken \
  -e ARB_CEX_SYMBOL=ETH/USD \
  -e ARB_DEX_CHAIN=ethereum \
  -e ARB_DEX_SELL=ETH \
  -e ARB_DEX_BUY=USDC \
  -e ARB_SELL_AMOUNT=0.05 \
  -e ARB_THRESHOLD_BPS=30 \
  -e ARB_POLL_SEC=5 \
  -v "$(pwd)/data:/data" \
  otomic-algo:local
```

Optional (enable 0x v2 quotes):

```bash
-e ZEROX_API_KEY="YOUR_0X_KEY"
```

Outputs:

* prints JSON-like dicts containing `edge_bps` and `trigger`
* appends signals to `./data/arb_signals.jsonl`

---

## Olares deployment (high-level)

Deploy as “Port your own container to Olares”:

* Image: your pushed image
* Port: `8080`
* Env:

  * `FT_CONFIG=/freqtrade/config/<exchange>.json`
  * `FT_STRATEGY=<StrategyName>`
  * `DISABLE_TRADING=1` (recommended default for dry-run)
* Multi-exchange: deploy multiple instances, each with a different `FT_CONFIG`.

---

## Safety

* Default recommendation: `DISABLE_TRADING=1` (dry-run)
* Martingale strategy is included as a guarded template only. Use with strict caps and risk controls.

