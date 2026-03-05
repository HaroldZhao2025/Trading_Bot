import os
import time
from typing import Dict, Any

from .execution_adapters import CexCcxtAdapter, Dex0xAdapter, DexScreenerAdapter, token_map, to_base_units, safe_write_jsonl

DEFAULT_LOG_PATH = "/data/arb_signals.jsonl"


def env(k: str, d: str) -> str:
    return os.environ.get(k, d)


def fenv(k: str, d: float) -> float:
    try:
        return float(os.environ.get(k, str(d)))
    except Exception:
        return d


def ienv(k: str, d: int) -> int:
    try:
        return int(os.environ.get(k, str(d)))
    except Exception:
        return d


def run() -> None:
    cex = env("ARB_CEX_EXCHANGE", "kraken")
    cex_symbol = env("ARB_CEX_SYMBOL", "ETH/USD")

    chain = env("ARB_DEX_CHAIN", "ethereum")
    sell = env("ARB_DEX_SELL", "ETH")
    buy = env("ARB_DEX_BUY", "USDC")

    sell_amount = fenv("ARB_SELL_AMOUNT", 0.05)
    sell_decimals = ienv("ARB_SELL_DECIMALS", 18)
    buy_decimals = ienv("ARB_BUY_DECIMALS", 6)

    threshold_bps = fenv("ARB_THRESHOLD_BPS", 30.0)
    poll_sec = fenv("ARB_POLL_SEC", 5.0)

    log_path = env("ARB_LOG_PATH", DEFAULT_LOG_PATH)

    cex_adapter = CexCcxtAdapter(cex)
    chain_id = ienv("ARB_CHAIN_ID", 1)
    dex_adapter = Dex0xAdapter(chain)
    ds = DexScreenerAdapter()

    tm = token_map(chain)
    sell_token = tm.get(sell.upper(), sell)
    buy_token = tm.get(buy.upper(), buy)

    sell_base = to_base_units(sell_amount, sell_decimals)

    while True:
        try:
            cex_px = cex_adapter.fetch_mid(cex_symbol)
            dex_source = "0x-v2"
            try:
                dq = dex_adapter.quote(sell_token, buy_token, sell_base, chain_id=chain_id)
                dex_buy = dq.buy_amount / (10 ** buy_decimals)
                dex_implied = dex_buy / sell_amount if sell_amount > 0 else 0.0
            except Exception as e:
                dex_source = f"dexscreener({type(e).__name__})"
                dex_implied = ds.implied_price(sell_token, buy_token)

            cex_mid = cex_px.mid
            if cex_mid <= 0:
                time.sleep(poll_sec)
                continue

            dex_minus_cex = (dex_implied - cex_mid) / cex_mid
            edge_bps = dex_minus_cex * 10000.0

            out: Dict[str, Any] = {
                "ts": time.time(),
                "cex": {"exchange": cex, "symbol": cex_symbol, "mid": cex_mid, "bid": cex_px.bid, "ask": cex_px.ask},
                "dex": {"chain": chain, "source": dex_source, "sell": sell_token, "buy": buy_token, "sell_amount": sell_amount, "implied": dex_implied},
                "edge_bps": edge_bps,
                "trigger": abs(edge_bps) >= threshold_bps,
            }

            print(out, flush=True)
            try:
                safe_write_jsonl(log_path, out)
            except Exception:
                pass

            time.sleep(poll_sec)
        except KeyboardInterrupt:
            return
        except Exception as e:
            print({"ts": time.time(), "error": str(e)}, flush=True)
            time.sleep(max(poll_sec, 2.0))