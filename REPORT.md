# Otomic Edge Algorithm – Crypto Trading Bots Pack (Olares-ready)

## 1. Objective
Deliver a runnable **Algorithm** module (as in Otomic edge client architecture) that can run on Olares directly:
- Algorithm runs as a container service on the edge side (close to wallet/keys).
- External connectivity is via exchange APIs (CEX). This matches the “edge Algorithm + external providers” concept in the Otomic architecture.  
- Provide a strategy pack (“trading bots”) implementing popular crypto bot styles.

## 2. What is delivered
This repo ports a mature open-source trading engine as the Algorithm runtime and ships a bot pack as strategy plug-ins.

### 2.1 Runtime / Engine
- **Freqtrade (Python)** as the execution engine: scheduling loop, market data ingestion, strategy callbacks, dry-run/live mode, trade DB, API server.

### 2.2 Strategy plug-ins (Bot Pack)
All bots are implemented as Freqtrade strategies under:
- `user_data/strategies/*.py`

Current bot pack (8):
1) `GridSimple` – grid-like range trading around SMA
2) `MartingaleGuarded` – martingale-style DCA with strict caps (high risk template)
3) `CtaTrend` – CTA trend-following via SMA crossover
4) `DcaAccumulator` – DCA accumulation with RSI filter
5) `DonchianBreakout` – channel breakout (Donchian)
6) `BollingerMR` – Bollinger band mean reversion (BB + RSI)
7) `RsiMeanReversion` – RSI mean reversion template
8) `AtrBreakout` – volatility breakout using ATR + trend filter

### 2.3 Multi-exchange configs
Configs live under `config/`:
- `config.json` – default / (commonly used for Binance or base template)
- `kraken.json` – Kraken dry-run validated locally
- `coinbase.json` – Coinbase template
- `bybit.json` – Bybit template

**Design choice:** Freqtrade runs **one exchange per process**, therefore multi-exchange support is implemented as:
- one config per exchange
- multiple instances (containers) running in parallel (different ports)  
This maps naturally to Olares deployment where each exchange runs as one app instance.

## 3. Olares deployment model (direct run)
Deploy the container through Olares Studio “Port your own container to Olares”:
- Image: your built image
- Port: 8080
- Env:
  - `FT_CONFIG=/freqtrade/config/<exchange>.json`
  - `FT_STRATEGY=<StrategyClassName>`
  - `DISABLE_TRADING=1` (recommended default; forces dry-run)
- Optional persistence:
  - mount `/data` and set `DATA_DIR=/data` if you want persistent runtime artifacts/DB/logs

## 4. Validation evidence
### 4.1 Offline validation (no exchange access required)
- `offline_validate.py` auto-discovers strategies in `user_data/strategies` and executes:
  - `populate_indicators`
  - `populate_entry_trend`
  - `populate_exit_trend`
This confirms each bot’s logic runs without touching exchange APIs.

### 4.2 Live dry-run validation (Kraken)
A Kraken dry-run run was validated locally:
- API server started and listened on `0.0.0.0:8080`
- Pairlist refresh succeeded (BTC/USD, ETH/USD)
- Strategy loaded successfully (GridSimple)
- Dry-run orders were created after signals were generated
- Graceful shutdown cancels open orders and stops API server cleanly

## 5. Safety defaults
- Default recommendation: `DISABLE_TRADING=1` to force dry-run.
- Martingale is included as a guarded template only; it must remain constrained (max steps, stoploss).
- Limit-only order configuration is used in exchange configs to keep behavior deterministic.