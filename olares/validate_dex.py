import argparse
import json
import traceback

from .dex.registry import chain_cfg, resolve_token
from .dex.dexscreener import DexScreenerAdapter
from .dex.zerox import ZeroXAdapter
from .dex.hyperliquid import HyperliquidAdapter
from .dex.router import DexRouter


def offline_checks():
    checks = []
    try:
        checks.append({"name": "chain_cfg(ethereum)", "ok": chain_cfg("ethereum")["chain_id"] == 1})
        checks.append({"name": "resolve_token(ETH)", "ok": resolve_token("ethereum", "ETH").startswith("0x")})
        DexScreenerAdapter()
        checks.append({"name": "DexScreenerAdapter()", "ok": True})
        ZeroXAdapter("ethereum")
        checks.append({"name": "ZeroXAdapter()", "ok": True})
        HyperliquidAdapter()
        checks.append({"name": "HyperliquidAdapter()", "ok": True})
        DexRouter("ethereum")
        checks.append({"name": "DexRouter()", "ok": True})
    except Exception as e:
        checks.append({"name": "offline_init", "ok": False, "error": str(e), "trace": traceback.format_exc(limit=4)})
    return checks


def online_checks():
    checks = []
    try:
        ds = DexScreenerAdapter()
        q = ds.implied_price("ethereum", "ETH", "USDC", 0.05)
        checks.append({"name": "DexScreener implied ETH/USDC", "ok": q.implied_price > 0, "venue": q.venue, "price": q.implied_price})
    except Exception as e:
        checks.append({"name": "DexScreener implied ETH/USDC", "ok": False, "error": str(e)})

    try:
        hl = HyperliquidAdapter(testnet=False)
        meta = hl.spot_meta()
        checks.append({"name": "Hyperliquid spotMeta", "ok": "tokens" in meta and "universe" in meta})
    except Exception as e:
        checks.append({"name": "Hyperliquid spotMeta", "ok": False, "error": str(e)})

    try:
        hl = HyperliquidAdapter(testnet=False)
        mids = hl.perp_all_mids()
        checks.append({"name": "Hyperliquid allMids", "ok": isinstance(mids, dict)})
    except Exception as e:
        checks.append({"name": "Hyperliquid allMids", "ok": False, "error": str(e)})

    try:
        zx = ZeroXAdapter("ethereum")
        checks.append({"name": "0x adapter init", "ok": True, "has_key": bool(zx.api_key)})
    except Exception as e:
        checks.append({"name": "0x adapter init", "ok": False, "error": str(e)})

    return checks


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--online", action="store_true")
    args = p.parse_args()

    checks = offline_checks()
    if args.online:
        checks.extend(online_checks())

    for x in checks:
        print(json.dumps(x, ensure_ascii=False), flush=True)

    if any(not x.get("ok", False) for x in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()